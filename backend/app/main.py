from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

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
    TTSRequest,
    TurnResponse,
    WhiteboardSnapshotMeta,
)
from app.phase_machine import get_phase_for_elapsed, should_inject_curveball
from app.storage import Storage
from app.tts import synthesize_elevenlabs

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
        "elevenlabs_available": settings.elevenlabs_configured,
        "elevenlabs_voice_id": settings.elevenlabs_voice_id if settings.elevenlabs_configured else None,
    }


@app.post("/api/tts")
async def text_to_speech(payload: TTSRequest) -> Response:
    if not settings.elevenlabs_configured:
        raise HTTPException(
            status_code=400,
            detail="ElevenLabs TTS is not configured. Set ELEVENLABS_API_KEY in .env.",
        )
    try:
        audio_bytes = await synthesize_elevenlabs(text=payload.text, voice_id=payload.voice_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return Response(content=audio_bytes, media_type="audio/mpeg")


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

    tts_provider = (
        payload.tts_provider
        if (payload.tts_provider == "elevenlabs" and settings.elevenlabs_configured)
        else "browser"
    )
    session = storage.create_session(
        case_packet=case_packet,
        reading_grace_seconds=payload.reading_grace_seconds,
        silence_nudge_seconds=payload.silence_nudge_seconds,
        tts_enabled=payload.tts_enabled,
        tts_provider=tts_provider,
        whiteboard_enabled=payload.whiteboard_enabled,
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
    whiteboard_png: Optional[UploadFile] = File(None),
    whiteboard_diff: Optional[str] = Form(None),
    whiteboard_scene: Optional[str] = Form(None),
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

    wb_png_bytes: Optional[bytes] = None
    if whiteboard_png is not None:
        raw_png = await whiteboard_png.read()
        if raw_png:
            wb_png_bytes = raw_png

    wb_diff_parsed: Optional[dict[str, object]] = None
    wb_diff_summary: Optional[str] = None
    wb_element_count = 0
    if whiteboard_diff:
        try:
            wb_diff_parsed = json.loads(whiteboard_diff)
            if isinstance(wb_diff_parsed, dict):
                wb_diff_summary = str(wb_diff_parsed.get("summary") or "").strip() or None
                wb_element_count = int(wb_diff_parsed.get("element_count") or 0)
        except Exception:
            wb_diff_summary = whiteboard_diff[:300]

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
            whiteboard_png_bytes=wb_png_bytes,
            whiteboard_diff=wb_diff_parsed,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    now = datetime.now(timezone.utc)
    candidate_turn_id = uuid.uuid4().hex[:10]

    snapshot_meta: Optional[WhiteboardSnapshotMeta] = None
    if wb_png_bytes:
        snap_index = len(session.whiteboard_snapshots) + 1
        mins = elapsed_seconds // 60
        secs = elapsed_seconds % 60
        snap_filename = f"turn-{snap_index:02d}-{mins:02d}m{secs:02d}s.png"
        storage.save_whiteboard_snapshot(session_id, snap_filename, wb_png_bytes)
        snapshot_meta = WhiteboardSnapshotMeta(
            filename=snap_filename,
            turn_id=candidate_turn_id,
            phase=phase.id,
            elapsed_seconds=elapsed_seconds,
            element_count=wb_element_count,
            diff_summary=wb_diff_summary,
            timestamp=now,
        )
        session.whiteboard_snapshots.append(snapshot_meta)

    if whiteboard_scene:
        storage.save_whiteboard_scene(session_id, whiteboard_scene)
        session.has_final_excalidraw = True

    candidate_turn = TranscriptTurn(
        id=candidate_turn_id,
        role="candidate",
        speaker_name="You",
        speaker_role="Candidate",
        text=result.candidate_transcript,
        phase=phase.id,
        elapsed_seconds=elapsed_seconds,
        speaking_duration_seconds=round(speaking_duration_seconds, 1),
        timestamp=now,
        delivery_notes=result.delivery_notes,
        whiteboard_snapshot=snapshot_meta.filename if snapshot_meta else None,
        whiteboard_diff_summary=wb_diff_summary,
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
        whiteboard_snapshot=snapshot_meta,
        should_hard_stop=(phase.id == PhaseId.HARD_STOP),
    )


@app.post("/api/sessions/{session_id}/whiteboard", response_model=Optional[WhiteboardSnapshotMeta])
async def save_final_whiteboard(
    session_id: str,
    elapsed_seconds: int = Form(..., ge=0),
    element_count: int = Form(0, ge=0),
    whiteboard_png: Optional[UploadFile] = File(None),
    whiteboard_scene: Optional[str] = Form(None),
) -> Optional[WhiteboardSnapshotMeta]:
    session = storage.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    snapshot_meta: Optional[WhiteboardSnapshotMeta] = None
    if whiteboard_png is not None:
        png_bytes = await whiteboard_png.read()
        if png_bytes:
            phase = get_phase_for_elapsed(elapsed_seconds, session.duration_minutes)
            filename = "final.png"
            storage.save_whiteboard_snapshot(session_id, filename, png_bytes)
            snapshot_meta = WhiteboardSnapshotMeta(
                filename=filename,
                phase=phase.id,
                elapsed_seconds=elapsed_seconds,
                element_count=element_count,
                diff_summary="Final whiteboard state captured at session end.",
                timestamp=datetime.now(timezone.utc),
            )
            # Replace any prior final.png entry
            session.whiteboard_snapshots = [
                s for s in session.whiteboard_snapshots if s.filename != filename
            ]
            session.whiteboard_snapshots.append(snapshot_meta)

    if whiteboard_scene:
        storage.save_whiteboard_scene(session_id, whiteboard_scene)
        session.has_final_excalidraw = True

    storage.save_session(session)
    return snapshot_meta


@app.get("/api/sessions/{session_id}/snapshots/{filename}")
def get_whiteboard_snapshot(session_id: str, filename: str) -> FileResponse:
    path = storage.get_whiteboard_file(session_id, filename)
    if not path:
        raise HTTPException(status_code=404, detail="Whiteboard snapshot not found")
    media_type = "application/json" if filename.endswith(".excalidraw") else "image/png"
    return FileResponse(path=path, media_type=media_type, filename=filename)


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
    milestone_snapshots = storage.read_milestone_snapshots(session_id, max_count=4)
    session.debrief_markdown = generate_debrief(
        case_packet,
        session,
        whiteboard_snapshots=milestone_snapshots,
    )

    storage.save_session(session)
    return session
