from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.config import settings
from app.models import CasePacket, SessionState

logger = logging.getLogger(__name__)


def _compute_session_metrics(session: SessionState) -> dict[str, object]:
    candidate_turns = [t for t in session.turns if t.role == "candidate"]
    nudges = [t for t in session.turns if t.is_nudge]
    durations = [t.speaking_duration_seconds for t in candidate_turns if t.speaking_duration_seconds > 0]
    avg_turn_sec = round(sum(durations) / len(durations), 1) if durations else 0.0
    max_turn_sec = round(max(durations), 1) if durations else 0.0
    long_turns = sum(1 for d in durations if d >= 150.0)
    phases_covered = sorted({t.phase.value for t in candidate_turns})
    return {
        "candidate_turn_count": len(candidate_turns),
        "total_turns": len(session.turns),
        "nudge_count": len(nudges),
        "avg_turn_seconds": avg_turn_sec,
        "max_turn_seconds": max_turn_sec,
        "long_turns_over_2m30": long_turns,
        "elapsed_minutes": round(session.elapsed_seconds / 60.0, 1),
        "curveballs_handled": len(session.curveballs_injected),
        "whiteboard_enabled": session.whiteboard_enabled,
        "whiteboard_snapshot_count": len(session.whiteboard_snapshots),
        "phases_covered": phases_covered,
    }


def _format_full_transcript(session: SessionState) -> str:
    lines: list[str] = []
    for t in session.turns:
        mins = t.elapsed_seconds // 60
        secs = t.elapsed_seconds % 60
        dur = f" | spoke {t.speaking_duration_seconds:.0f}s" if t.speaking_duration_seconds else ""
        notes = f" | delivery: {t.delivery_notes}" if t.delivery_notes else ""
        wb = f" | whiteboard: {t.whiteboard_snapshot} ({t.whiteboard_diff_summary or 'captured'})" if t.whiteboard_snapshot else ""
        lines.append(f"[{mins:02d}:{secs:02d} | {t.phase.value}{dur}{wb}] {t.speaker_name} ({t.role}): {t.text}{notes}")
    return "\n".join(lines) or "(No turns recorded.)"


def _demo_debrief(case_packet: CasePacket, session: SessionState) -> str:
    metrics = _compute_session_metrics(session)
    date_str = datetime.now(timezone.utc).strftime("%d %B %Y")
    candidate_turns = [t for t in session.turns if t.role == "candidate"]

    if metrics["candidate_turn_count"] == 0:
        verdict = "Needs Drill (Incomplete Session)"
        summary = (
            "No spoken candidate turns were recorded during this session. "
            "Run a full Push-to-Talk walkthrough so the Evaluator can score your structure, thinking-out-loud discipline, and trade-off rigor."
        )
    elif metrics["candidate_turn_count"] < 3:
        verdict = "Needs Drill (Short Practice Run)"
        summary = (
            f"You completed {metrics['candidate_turn_count']} spoken turns across {metrics['elapsed_minutes']} minutes in Demo Mode. "
            "To unlock live Gemini scoring with tone/hesitation feedback and verbatim turn-by-turn coaching, set `GEMINI_API_KEY` in `.env`."
        )
    else:
        verdict = "Lean Hire (Demo Mode Estimate)"
        summary = (
            f"You completed {metrics['candidate_turn_count']} spoken turns across {metrics['elapsed_minutes']} minutes "
            f"(avg turn {metrics['avg_turn_seconds']}s, {metrics['nudge_count']} silence nudges). "
            "Set `GEMINI_API_KEY` in `.env` for deep LLM-powered critique of your exact Sokin product sense, trade-offs, and upgrade answers."
        )

    sample_replays = []
    for idx, turn in enumerate(candidate_turns[:3], start=1):
        mins = turn.elapsed_seconds // 60
        secs = turn.elapsed_seconds % 60
        snippet = turn.text[:180] + ("..." if len(turn.text) > 180 else "")
        sample_replays.append(
            f"### Turning Point {idx} — `{mins:02d}:{secs:02d}` ({turn.phase.value})\n"
            f"- **What you said:** \"{snippet}\"\n"
            f"- **Coaching note:** Anchor your opening sentence with a crisp signpost (*\"I'll cover three things: constraints, architecture, and sequencing\"*) before diving into details.\n"
            f"- **30-Second Upgrade Answer:** *\"Before prioritising API foundation vs. MCP, let me clarify two constraints: squad capacity and compliance sign-off gates. Once confirmed, I'll separate gateway-enforced Core controls from Application DX improvements so we unblock the stalled partner while de-risking agentic execution.\"*"
        )
    replay_md = "\n\n".join(sample_replays) if sample_replays else "_No candidate turns recorded to replay._"

    focus_list = "\n".join(f"- {item}" for item in case_packet.evaluation_focus)

    return f"""# Post-Interview Debrief: {case_packet.title}

**Company:** {case_packet.company}  
**Role:** {case_packet.role}  
**Date:** {date_str}  
**Mode:** Demo Mode (configure `GEMINI_API_KEY` in `.env` for full Gemini Evaluator analysis)

---

## 1. Overall Readiness Verdict: **{verdict}**

{summary}

### Session Telemetry
| Metric | Value |
|---|---|
| Elapsed Time | {metrics['elapsed_minutes']} / {case_packet.duration_minutes} min |
| Spoken Turns | {metrics['candidate_turn_count']} |
| Average Turn Length | {metrics['avg_turn_seconds']}s (max {metrics['max_turn_seconds']}s) |
| Turns Over 2:30 (Amber/Red) | {metrics['long_turns_over_2m30']} |
| Silence Nudges Triggered | {metrics['nudge_count']} |
| Curveballs Handled | {metrics['curveballs_handled']} / {len(case_packet.curveballs)} |
| Whiteboard Snapshots Captured | {metrics['whiteboard_snapshot_count']} ({'Enabled' if metrics['whiteboard_enabled'] else 'Audio-Only Mode'}) |

---

## 2. Dimension Scores (1–5)

| Dimension | Score | Evidence & Coaching |
|---|---|---|
| **Structure & Signposting** | 3 / 5 | State your 3-part agenda upfront on every major transition so the panel stays oriented. |
| **Thinking Out Loud** | {4 if metrics['nudge_count'] == 0 else 3} / 5 | {metrics['nudge_count']} silence nudges triggered. Keep narrating hypotheses even while weighing trade-offs. |
| **Clarity & Conciseness** | {4 if metrics['long_turns_over_2m30'] == 0 else 3} / 5 | Average spoken turn was {metrics['avg_turn_seconds']}s ({metrics['long_turns_over_2m30']} turns exceeded 2:30). Aim for 60–120s crisp turns. |
| **Product Sense & Trade-Off Rigor** | 3 / 5 | Connect DX fixes directly to Sokin's $90M→$120M run-rate, Core vs. App layer boundaries, and gateway-enforced Trust-by-Design. |
| **Whiteboard Effectiveness** | {('4 / 5' if metrics['whiteboard_snapshot_count'] > 0 else '2 / 5') if metrics['whiteboard_enabled'] else 'N/A'} | {f"{metrics['whiteboard_snapshot_count']} Excalidraw snapshot(s) captured. Anchor Core Platform vs. Application Layer boundaries visually as you narrate." if metrics['whiteboard_enabled'] else "Audio-Only Mode selected for this session."} |

---

## 3. Moment-by-Moment Replay

{replay_md}

---

## 4. Case Evaluation Checklist
{focus_list}

---

## 5. Targeted Drill for Next Session
1. **15-Minute Curveball Pushback Drill:** Practice responding to a CEO deadline vs. Compliance/Support collision in under 90 seconds without abandoning your core thesis—state what ships in 8 weeks, what slips, and the non-negotiable Trust-by-Design guardrail.
2. **2-Minute Executive Wrap-Up Drill:** Record a single uninterrupted 120-second CPO/CEO pitch ending with 3 measurable KPIs (TTFP, ticket deflection, scoped MCP production adoption).
"""


def generate_debrief(
    case_packet: CasePacket,
    session: SessionState,
    whiteboard_snapshots: list[tuple[str, bytes]] | None = None,
) -> str:
    """Generate the structured Markdown post-interview debrief (`debrief.md`), including multimodal whiteboard review."""
    if settings.demo_mode:
        return _demo_debrief(case_packet, session)

    from google import genai
    from google.genai import types

    metrics = _compute_session_metrics(session)
    transcript = _format_full_transcript(session)
    eval_focus = "\n".join(f"- {item}" for item in case_packet.evaluation_focus)
    hidden_facts = "\n".join(f"- {k}: {v}" for k, v in case_packet.hidden_facts.items())

    snapshot_names = [name for name, _ in (whiteboard_snapshots or [])]
    wb_context = (
        f"Attached whiteboard milestone PNG snapshots (in chronological order): {', '.join(snapshot_names)}."
        if snapshot_names
        else (
            "Whiteboard was enabled, but no drawings were captured during the session."
            if session.whiteboard_enabled
            else "Candidate ran this session in Audio-Only Mode (whiteboard disabled)."
        )
    )

    prompt = f"""You are a calibrated Bar-Raiser Product Management Interview Evaluator reviewing a voice-first Product Sense interview for {case_packet.company} ({case_packet.role}).

CASE TITLE: {case_packet.title}
EVALUATION FOCUS:
{eval_focus}

HIDDEN CASE FACTS (to judge whether the candidate uncovered key constraints):
{hidden_facts}

SESSION TELEMETRY:
{metrics}

WHITEBOARD EVIDENCE:
{wb_context}

FULL TIMESTAMPED TRANSCRIPT:
{transcript}

Write a rigorous, candid, actionable Markdown debrief following this exact structure:
1. `# Post-Interview Debrief: {case_packet.title}` with metadata header (Company, Role, Elapsed Time, Spoken Turns, Avg Turn Length, Silence Nudges, Whiteboard Snapshots).
2. `## 1. Overall Readiness Verdict` — Choose strictly one of **Strong Hire**, **Lean Hire**, or **Needs Drill**, followed by a sharp 3-sentence executive summary.
3. `## 2. Dimension Scores (1–5)` — Score each dimension 1–5 with concrete transcript & whiteboard evidence:
   - **Structure & Signposting**
   - **Thinking Out Loud**
   - **Clarity & Conciseness**
   - **Product Sense & Trade-Off Rigor**
   - **Whiteboard Effectiveness** (inspect the attached Excalidraw PNGs: did the diagram reinforce the spoken narrative, clearly separate Core vs. App layers / trade-offs, or leave key concepts undocumented/messy? Mark N/A only if Audio-Only Mode was selected)
4. `## 3. Moment-by-Moment Replay (Top 3–5 Turning Points)` — For each turning point, cite the exact timestamp, quote from the candidate, and reference the relevant whiteboard snapshot filename if applicable, explain why it worked or lost the room, and provide a concrete **30-Second Upgrade Answer** phrased crisply in first person.
5. `## 4. Targeted Drill for Next Session` — 1–2 concrete micro-drills tailored directly to their biggest gap in this session.

Be direct, high-bar, and specific to {case_packet.company}. Do not flatter generic answers."""

    contents: list[object] = [prompt]
    for name, png_bytes in (whiteboard_snapshots or []):
        contents.append(f"Whiteboard snapshot: {name}")
        contents.append(types.Part.from_bytes(data=png_bytes, mime_type="image/png"))

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_evaluator_model,
            contents=contents,
            config=types.GenerateContentConfig(temperature=0.35),
        )
        text = (response.text or "").strip()
        if not text:
            return _demo_debrief(case_packet, session)
        return text
    except Exception as exc:
        logger.exception("Gemini evaluator failed, falling back to structured summary: %s", exc)
        return _demo_debrief(case_packet, session) + f"\n\n> _Note: Live Evaluator API call failed ({exc}); generated local telemetry fallback._\n"
