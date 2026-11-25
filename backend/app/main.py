from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.agents.evaluator import generate_debrief
from app.agents.interviewer import build_opening_turn, run_interviewer_turn
from app.config import settings
from app.models import (
    CandidateCaseView,
    CaseSummary,
    CreateSessionRequest,
    EndSessionRequest,
    NudgeRequest,
    PhaseId,
    SessionState,
    SessionSummary,
    TranscriptTurn,
    TurnResponse,
)
from app.phase_machine import get_phase_for_elapsed, should_inject_curveball
from app.storage import Storage

app = FastAPI(
    title="Product Sense Interview Harness API",
    version="0.1.0",
    description="Phase 1 local backend for voice-first Product Sense interview simulation.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage = Storage()


@app.get("/api/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "demo_mode": settings.demo_mode,
        "interviewer_model": settings.gemini_interviewer_model,
        "evaluator_model": settings.gemini_evaluator_model,
    }


@app.get("/api/cases", response_model=list[CaseSummary])
def list_cases() -> list[CaseSummary]:
    return storage.list_cases()


@app.get("/api/cases/{case_id}", response_model=CandidateCaseView)
def get_case(case_id: str) -> CandidateCaseView:
    view = storage.get_candidate_case_view(case_id)
    if not view:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
    return view


@app.get("/api/sessions", response_model=list[SessionSummary])
def list_sessions() -> list[SessionSummary]:
    return storage.list_sessions()


@app.post("/api/sessions", response_model=SessionState)
def create_session(payload: CreateSessionRequest) -> SessionState:
    case_packet = storage.get_case(payload.case_id)
    if not case_packet:
        raise HTTPException(status_code=404, detail=f"Case '{payload.case_id}' not found")

    session = storage.create_session(
        case_packet=case_packet,
        silence_nudge_seconds=payload.silence_nudge_seconds,
        tts_enabled=payload.tts_enabled,
        demo_mode=settings.demo_mode,
    )

    speaker_name, speaker_role, opening_text = build_opening_turn(case_packet)
    opening_turn = TranscriptTurn(
        id=uuid.uuid4().hex[:10],
        role="interviewer",
        speaker_name=speaker_name,
        speaker_role=speaker_role,
        text=opening_text,
        phase=session.current_phase.id,
        elapsed_seconds=0,
        timestamp=datetime.now(timezone.utc),
    )
    session.turns.append(opening_turn)
    storage.save_session(session)
    return session


@app.get("/api/sessions/{session_id}", response_model=SessionState)
def get_session(session_id: str) -> SessionState:
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return session


@app.post("/api/sessions/{session_id}/turn", response_model=TurnResponse)
async def submit_turn(
    session_id: str,
    elapsed_seconds: int = Form(..., ge=0),
    speaking_duration_seconds: float = Form(0.0, ge=0.0),
    audio: Optional[UploadFile] = File(None),
    demo_transcript: Optional[str] = Form(None),
) -> TurnResponse:
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    if session.status != "active":
        raise HTTPException(status_code=409, detail="Session has already ended")

    case_packet = storage.get_session_case_packet(session_id)
    if not case_packet:
        raise HTTPException(status_code=404, detail="Case packet for session not found")

    audio_bytes: Optional[bytes] = None
    audio_mime = "audio/webm"
    if audio is not None:
        audio_bytes = await audio.read()
        if audio.content_type:
            audio_mime = audio.content_type.split(";")[0].strip()

    if not settings.demo_mode and not audio_bytes and not demo_transcript:
        raise HTTPException(status_code=400, detail="Audio recording is required")

    phase = get_phase_for_elapsed(elapsed_seconds, session.duration_minutes)
    curveball_idx = should_inject_curveball(
        phase=phase,
        curveballs_injected=session.curveballs_injected,
        total_curveballs=len(case_packet.curveballs),
        elapsed_seconds=elapsed_seconds,
        duration_minutes=session.duration_minutes,
    )

    try:
        result = run_interviewer_turn(
            case_packet=case_packet,
            session=session,
            phase=phase,
            elapsed_seconds=elapsed_seconds,
            speaking_duration_seconds=speaking_duration_seconds,
            curveball_to_inject=curveball_idx,
            audio_bytes=audio_bytes,
            audio_mime_type=audio_mime,
            transcript_override=demo_transcript,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    now = datetime.now(timezone.utc)
    candidate_turn = TranscriptTurn(
        id=uuid.uuid4().hex[:10],
        role="candidate",
        speaker_name="You",
        speaker_role="Candidate",
        text=result.candidate_transcript,
        phase=phase.id,
        elapsed_seconds=elapsed_seconds,
        speaking_duration_seconds=round(speaking_duration_seconds, 1),
        timestamp=now,
        delivery_notes=result.delivery_notes,
    )
    interviewer_turn = TranscriptTurn(
        id=uuid.uuid4().hex[:10],
        role="interviewer",
        speaker_name=result.speaker_name,
        speaker_role=result.speaker_role,
        text=result.reply,
        phase=phase.id,
        elapsed_seconds=elapsed_seconds,
        timestamp=now,
        curveball_index=result.curveball_index,
    )

    session.turns.append(candidate_turn)
    session.turns.append(interviewer_turn)
    session.elapsed_seconds = max(session.elapsed_seconds, elapsed_seconds)
    session.current_phase = phase
    if result.curveball_index is not None and result.curveball_index not in session.curveballs_injected:
        session.curveballs_injected.append(result.curveball_index)

    storage.save_session(session)

    return TurnResponse(
        candidate_turn=candidate_turn,
        interviewer_turn=interviewer_turn,
        current_phase=phase,
        elapsed_seconds=session.elapsed_seconds,
        curveballs_injected=session.curveballs_injected,
        should_hard_stop=(phase.id == PhaseId.HARD_STOP),
    )


@app.post("/api/sessions/{session_id}/nudge", response_model=TranscriptTurn)
def record_silence_nudge(session_id: str, payload: NudgeRequest) -> TranscriptTurn:
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    if session.status != "active":
        raise HTTPException(status_code=409, detail="Session has already ended")

    phase = get_phase_for_elapsed(payload.elapsed_seconds, session.duration_minutes)
    lead = session.interviewers[0] if session.interviewers else None
    nudge_turn = TranscriptTurn(
        id=uuid.uuid4().hex[:10],
        role="interviewer",
        speaker_name=lead.name if lead else "Interviewer",
        speaker_role=lead.role if lead else "Panel",
        text="Take a second to narrate what you're weighing right now — even if it's rough.",
        phase=phase.id,
        elapsed_seconds=payload.elapsed_seconds,
        timestamp=datetime.now(timezone.utc),
        is_nudge=True,
    )
    session.turns.append(nudge_turn)
    session.elapsed_seconds = max(session.elapsed_seconds, payload.elapsed_seconds)
    session.current_phase = phase
    storage.save_session(session)
    return nudge_turn


@app.post("/api/sessions/{session_id}/end", response_model=SessionState)
def end_session(session_id: str, payload: EndSessionRequest) -> SessionState:
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    if session.status == "completed" and session.debrief_markdown:
        return session

    case_packet = storage.get_session_case_packet(session_id)
    if not case_packet:
        raise HTTPException(status_code=404, detail="Case packet for session not found")

    session.elapsed_seconds = max(session.elapsed_seconds, payload.elapsed_seconds)
    session.current_phase = get_phase_for_elapsed(session.elapsed_seconds, session.duration_minutes)
    session.status = "completed"
    session.ended_at = datetime.now(timezone.utc)
    session.debrief_markdown = generate_debrief(case_packet, session)

    storage.save_session(session)
    return session
