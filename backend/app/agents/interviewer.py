from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Optional

from app.config import settings
from app.models import CasePacket, PhaseId, PhaseInfo, SessionState

logger = logging.getLogger(__name__)


@dataclass
class InterviewerTurnResult:
    candidate_transcript: str
    delivery_notes: Optional[str]
    speaker_name: str
    speaker_role: str
    reply: str
    curveball_index: Optional[int] = None


def build_opening_turn(case_packet: CasePacket) -> tuple[str, str, str]:
    """Build a concise, realistic spoken opening from the lead interviewer."""
    lead = case_packet.interviewers[0]
    co_names = [p.name for p in case_packet.interviewers[1:]]
    co_intro = (
        f" I'm joined by {', '.join(co_names)} from Engineering."
        if co_names
        else ""
    )
    opening = (
        f"Hi, I'm {lead.name}, {lead.role} at {case_packet.company}.{co_intro} "
        f"Thanks for doing this {case_packet.duration_minutes}-minute product sense case with us. "
        f"You have the brief in front of you — take a moment to review it, think out loud as you go, "
        f"and start by asking any clarifying questions you need before framing your approach."
    )
    return lead.name, lead.role, opening


def _format_history(session: SessionState) -> str:
    if not session.turns:
        return "(No prior turns yet.)"
    lines: list[str] = []
    for t in session.turns[-16:]:
        mins = t.elapsed_seconds // 60
        secs = t.elapsed_seconds % 60
        tag = f"[{mins:02d}:{secs:02d} | {t.phase.value}]"
        if t.role == "candidate":
            dur = f" ({t.speaking_duration_seconds:.0f}s)" if t.speaking_duration_seconds else ""
            lines.append(f"{tag} Candidate{dur}: {t.text}")
        elif t.role == "interviewer":
            lines.append(f"{tag} {t.speaker_name} ({t.speaker_role}): {t.text}")
        else:
            lines.append(f"{tag} [System]: {t.text}")
    return "\n".join(lines)


def _build_interviewer_prompt(
    case_packet: CasePacket,
    session: SessionState,
    phase: PhaseInfo,
    elapsed_seconds: int,
    speaking_duration_seconds: float,
    curveball_to_inject: Optional[int],
    transcript_override: Optional[str] = None,
) -> str:
    personas_text = "\n".join(
        f"- {p.name} ({p.role}): Focuses on {p.focus}" for p in case_packet.interviewers
    )
    hidden_facts_text = "\n".join(
        f"- {k}: {v}" for k, v in case_packet.hidden_facts.items()
    )
    eval_focus_text = "\n".join(f"- {item}" for item in case_packet.evaluation_focus)

    elapsed_min = elapsed_seconds / 60.0
    remaining_min = max(0.0, case_packet.duration_minutes - elapsed_min)

    curveball_instruction = ""
    if curveball_to_inject is not None and 0 <= curveball_to_inject < len(case_packet.curveballs):
        cb_text = case_packet.curveballs[curveball_to_inject]
        curveball_instruction = (
            f"\nMANDATORY CURVEBALL FOR THIS TURN:\n"
            f"You MUST introduce the following realistic stakeholder pushback naturally in your reply:\n"
            f'"{cb_text}"\n'
        )

    audio_instruction = (
        f'The candidate said (text override): "{transcript_override}"'
        if transcript_override
        else "Listen carefully to the attached audio clip of the candidate's spoken turn. Transcribe it faithfully (including meaningful pauses or filler words if notable) and note any delivery observations (pace, clarity, hesitation, signposting)."
    )

    return f"""You are roleplaying an active, realistic senior PM interview panel for {case_packet.company} ({case_packet.role}).

PANEL PERSONAS (pick the single most relevant speaker for this turn):
{personas_text}

CASE BRIEF (known to candidate):
{case_packet.candidate_brief_markdown}

HIDDEN FACTS (ONLY reveal facts when the candidate explicitly asks a relevant clarifying question — NEVER volunteer unasked hidden facts):
{hidden_facts_text}

EVALUATION FOCUS:
{eval_focus_text}

TIMING & PHASE STATE MACHINE:
- Elapsed: {elapsed_min:.1f} min / {case_packet.duration_minutes} min ({remaining_min:.1f} min remaining)
- Current Phase ({phase.number}/6): {phase.name}
- Phase Objective: {phase.objective}
- Required Interviewer Behaviour: {phase.interviewer_behavior}
- Candidate's last turn speaking duration: {speaking_duration_seconds:.1f} seconds
{curveball_instruction}

CONVERSATION HISTORY:
{_format_history(session)}

CANDIDATE'S NEW TURN:
{audio_instruction}

INSTRUCTIONS FOR YOUR REPLY:
1. Stay strictly in character as one of the panel interviewers.
2. Keep your spoken reply crisp, natural, and conversational — **2 to 4 sentences (~15–30 seconds when read aloud)**. Never lecture or give away the answer.
3. Push back on hand-waving, unexamined assumptions, or missing constraints (e.g. compliance, engineering capacity, gateway enforcement, sandbox parity, commercial trade-offs).
4. If the candidate jumped straight into solutions in Phase 1 without clarifying, gently nudge them to check constraints first.
5. If we are in Phase 5 (Executive Wrap-Up), ask for or react to a crisp 2-minute CPO/CEO pitch.
6. If we are in Phase 6 (Hard Stop), close the interview warmly and concisely.

Return ONLY valid JSON matching this exact schema:
{{
  "candidate_transcript": "verbatim transcript of what the candidate said",
  "delivery_notes": "short 1-sentence note on tone, pacing, clarity, or hesitation (for post-session debrief only)",
  "speaker_name": "name of the interviewer speaking (from PANEL PERSONAS)",
  "speaker_role": "role of that interviewer",
  "reply": "your concise 2-4 sentence spoken interviewer response"
}}"""


def _demo_interviewer_turn(
    case_packet: CasePacket,
    session: SessionState,
    phase: PhaseInfo,
    curveball_to_inject: Optional[int],
    transcript_override: Optional[str] = None,
    speaking_duration_seconds: float = 0.0,
) -> InterviewerTurnResult:
    """Deterministic local fallback when GEMINI_API_KEY is not set."""
    candidate_text = (
        transcript_override.strip()
        if transcript_override and transcript_override.strip()
        else (
            f"[Demo Mode audio clip — {speaking_duration_seconds:.1f}s recorded. "
            "Configure GEMINI_API_KEY in .env for live Gemini audio transcription.]"
        )
    )

    lead = case_packet.interviewers[0]
    eng = case_packet.interviewers[1] if len(case_packet.interviewers) > 1 else lead

    lowered = candidate_text.lower()

    if curveball_to_inject is not None and 0 <= curveball_to_inject < len(case_packet.curveballs):
        cb = case_packet.curveballs[curveball_to_inject]
        speaker = eng if curveball_to_inject == 0 else lead
        return InterviewerTurnResult(
            candidate_transcript=candidate_text,
            delivery_notes="Demo mode: live audio delivery analysis requires GEMINI_API_KEY.",
            speaker_name=speaker.name,
            speaker_role=speaker.role,
            reply=f"Hold on — let me throw a real constraint at you. {cb} How does that change your sequencing?",
            curveball_index=curveball_to_inject,
        )

    # Check if candidate asked about a hidden fact
    if any(w in lowered for w in ["team", "engineer", "capacity", "headcount", "squad", "writer"]):
        fact = case_packet.hidden_facts.get("engineering_capacity") or case_packet.hidden_facts.get("team_constraints")
        if fact:
            return InterviewerTurnResult(
                candidate_transcript=candidate_text,
                delivery_notes="Asked about engineering capacity early — good clarifying instinct.",
                speaker_name=lead.name,
                speaker_role=lead.role,
                reply=f"Good question. {fact} Given that constraint, what else do you want to know before framing your strategy?",
            )

    if any(w in lowered for w in ["sandbox", "error", "ticket", "drift", "ttfp", "support"]):
        fact = case_packet.hidden_facts.get("current_api_state") or case_packet.hidden_facts.get("support_ticket_drivers")
        if fact:
            return InterviewerTurnResult(
                candidate_transcript=candidate_text,
                delivery_notes="Probed API/sandbox ground truth before proposing solutions.",
                speaker_name=eng.name,
                speaker_role=eng.role,
                reply=f"Here's the honest picture from our side: {fact} How does that shape what you'd tackle first?",
            )

    if any(w in lowered for w in ["mcp", "agent", "compliance", "security", "audit", "limit"]):
        fact = case_packet.hidden_facts.get("compliance_stance") or case_packet.hidden_facts.get("mcp_current_state")
        if fact:
            return InterviewerTurnResult(
                candidate_transcript=candidate_text,
                delivery_notes="Surfaced compliance/security constraints on agentic execution.",
                speaker_name=eng.name,
                speaker_role=eng.role,
                reply=f"Glad you brought that up. {fact} Where in the stack would you enforce those controls so we aren't relying on prompt instructions?",
            )

    # Phase-based default probing
    if phase.id == PhaseId.BRIEF_CLARIFY:
        return InterviewerTurnResult(
            candidate_transcript=candidate_text,
            delivery_notes="Demo mode active.",
            speaker_name=lead.name,
            speaker_role=lead.role,
            reply="Got it. Before you lock into a solution, are there any constraints around engineering capacity, current commercial pipeline, or compliance guardrails you'd like to clarify?",
        )
    if phase.id == PhaseId.FRAMING_STRATEGY:
        return InterviewerTurnResult(
            candidate_transcript=candidate_text,
            delivery_notes="Demo mode active.",
            speaker_name=lead.name,
            speaker_role=lead.role,
            reply="Walk me through your strategic framing: who are we optimising for over the next two quarters, why now, and what are you explicitly choosing NOT to solve?",
        )
    if phase.id == PhaseId.DEEP_DIVE:
        return InterviewerTurnResult(
            candidate_transcript=candidate_text,
            delivery_notes="Demo mode active.",
            speaker_name=eng.name,
            speaker_role=eng.role,
            reply="Push deeper on the architecture for me. Which parts belong in the Core Platform / Gateway layer versus the Application DX layer, and how do you prevent a looping agent or drifting mock from breaking trust?",
        )
    if phase.id == PhaseId.CURVEBALL:
        return InterviewerTurnResult(
            candidate_transcript=candidate_text,
            delivery_notes="Demo mode active.",
            speaker_name=lead.name,
            speaker_role=lead.role,
            reply="I hear the compromise, but push back on yourself — if we cut scope there, what is the biggest operational or commercial risk we're accepting, and how do we mitigate it?",
        )
    if phase.id == PhaseId.EXECUTIVE_WRAPUP:
        return InterviewerTurnResult(
            candidate_transcript=candidate_text,
            delivery_notes="Demo mode active.",
            speaker_name=lead.name,
            speaker_role=lead.role,
            reply="We have just a few minutes left. Give me your crisp 2-minute pitch to the CPO and CEO: your final recommendation, 2-quarter sequencing, and the 2–3 metrics you'll be held accountable for.",
        )

    return InterviewerTurnResult(
        candidate_transcript=candidate_text,
        delivery_notes="Demo mode active.",
        speaker_name=lead.name,
        speaker_role=lead.role,
        reply="That brings us to time — thank you for walking us through your thinking. Let's wrap up here and generate your structured debrief.",
    )


def run_interviewer_turn(
    case_packet: CasePacket,
    session: SessionState,
    phase: PhaseInfo,
    elapsed_seconds: int,
    speaking_duration_seconds: float,
    curveball_to_inject: Optional[int],
    audio_bytes: Optional[bytes] = None,
    audio_mime_type: str = "audio/webm",
    transcript_override: Optional[str] = None,
) -> InterviewerTurnResult:
    """Process one Push-to-Talk candidate turn and return transcript + interviewer response."""
    if settings.demo_mode:
        return _demo_interviewer_turn(
            case_packet=case_packet,
            session=session,
            phase=phase,
            curveball_to_inject=curveball_to_inject,
            transcript_override=transcript_override,
            speaking_duration_seconds=speaking_duration_seconds,
        )

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = _build_interviewer_prompt(
        case_packet=case_packet,
        session=session,
        phase=phase,
        elapsed_seconds=elapsed_seconds,
        speaking_duration_seconds=speaking_duration_seconds,
        curveball_to_inject=curveball_to_inject,
        transcript_override=transcript_override,
    )

    contents: list[object] = [prompt]
    if audio_bytes and not transcript_override:
        contents.append(types.Part.from_bytes(data=audio_bytes, mime_type=audio_mime_type))

    try:
        response = client.models.generate_content(
            model=settings.gemini_interviewer_model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.5,
            ),
        )
        raw_text = (response.text or "").strip()
        data = json.loads(raw_text)
        lead = case_packet.interviewers[0]
        return InterviewerTurnResult(
            candidate_transcript=str(data.get("candidate_transcript") or transcript_override or "(inaudible)").strip(),
            delivery_notes=str(data.get("delivery_notes") or "").strip() or None,
            speaker_name=str(data.get("speaker_name") or lead.name).strip(),
            speaker_role=str(data.get("speaker_role") or lead.role).strip(),
            reply=str(data.get("reply") or "Could you elaborate on the core trade-off you're making there?").strip(),
            curveball_index=curveball_to_inject,
        )
    except Exception as exc:
        logger.exception("Gemini interviewer turn failed: %s", exc)
        raise RuntimeError(f"Interviewer agent error: {exc}") from exc
