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
        "phases_covered": phases_covered,
    }


def _format_full_transcript(session: SessionState) -> str:
    lines: list[str] = []
    for t in session.turns:
        mins = t.elapsed_seconds // 60
        secs = t.elapsed_seconds % 60
        dur = f" | spoke {t.speaking_duration_seconds:.0f}s" if t.speaking_duration_seconds else ""
        notes = f" | delivery: {t.delivery_notes}" if t.delivery_notes else ""
        lines.append(f"[{mins:02d}:{secs:02d} | {t.phase.value}{dur}] {t.speaker_name} ({t.role}): {t.text}{notes}")
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

---

## 2. Dimension Scores (1–5)

| Dimension | Score | Evidence & Coaching |
|---|---|---|
| **Structure & Signposting** | 3 / 5 | State your 3-part agenda upfront on every major transition so the panel stays oriented. |
| **Thinking Out Loud** | {4 if metrics['nudge_count'] == 0 else 3} / 5 | {metrics['nudge_count']} silence nudges triggered. Keep narrating hypotheses even while weighing trade-offs. |
| **Clarity & Conciseness** | {4 if metrics['long_turns_over_2m30'] == 0 else 3} / 5 | Average spoken turn was {metrics['avg_turn_seconds']}s ({metrics['long_turns_over_2m30']} turns exceeded 2:30). Aim for 60–120s crisp turns. |
| **Product Sense & Trade-Off Rigor** | 3 / 5 | Connect DX fixes directly to Sokin's $90M→$120M run-rate, Core vs. App layer boundaries, and gateway-enforced Trust-by-Design. |
| **Visual / Whiteboard Readiness (Phase 2)** | N/A | Audio-only Phase 1 session. Practice verbalising architectural boundaries clearly in preparation for Excalidraw in Phase 2. |

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


def generate_debrief(case_packet: CasePacket, session: SessionState) -> str:
    """Generate the structured Markdown post-interview debrief (`debrief.md`)."""
    if settings.demo_mode:
        return _demo_debrief(case_packet, session)

    from google import genai
    from google.genai import types

    metrics = _compute_session_metrics(session)
    transcript = _format_full_transcript(session)
    eval_focus = "\n".join(f"- {item}" for item in case_packet.evaluation_focus)
    hidden_facts = "\n".join(f"- {k}: {v}" for k, v in case_packet.hidden_facts.items())

    prompt = f"""You are a calibrated Bar-Raiser Product Management Interview Evaluator reviewing a voice-first Product Sense interview for {case_packet.company} ({case_packet.role}).

CASE TITLE: {case_packet.title}
EVALUATION FOCUS:
{eval_focus}

HIDDEN CASE FACTS (to judge whether the candidate uncovered key constraints):
{hidden_facts}

SESSION TELEMETRY:
{metrics}

FULL TIMESTAMPED TRANSCRIPT:
{transcript}

Write a rigorous, candid, actionable Markdown debrief following this exact structure:
1. `# Post-Interview Debrief: {case_packet.title}` with metadata header (Company, Role, Elapsed Time, Spoken Turns, Avg Turn Length, Silence Nudges).
2. `## 1. Overall Readiness Verdict` — Choose strictly one of **Strong Hire**, **Lean Hire**, or **Needs Drill**, followed by a sharp 3-sentence executive summary.
3. `## 2. Dimension Scores (1–5)` — Score each dimension 1–5 with concrete transcript evidence:
   - **Structure & Signposting**
   - **Thinking Out Loud**
   - **Clarity & Conciseness**
   - **Product Sense & Trade-Off Rigor**
   - **Architectural & Trust-by-Design Clarity** (note Phase 1 is audio-only; assess how clearly they communicated Core vs. App boundaries verbally)
4. `## 3. Moment-by-Moment Replay (Top 3–5 Turning Points)` — For each turning point, cite the exact timestamp and quote from the candidate, explain why it worked or lost the room, and provide a concrete **30-Second Upgrade Answer** phrased crisply in first person.
5. `## 4. Targeted Drill for Next Session` — 1–2 concrete micro-drills tailored directly to their biggest gap in this session.

Be direct, high-bar, and specific to {case_packet.company}. Do not flatter generic answers."""

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_evaluator_model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.35),
        )
        text = (response.text or "").strip()
        if not text:
            return _demo_debrief(case_packet, session)
        return text
    except Exception as exc:
        logger.exception("Gemini evaluator failed, falling back to structured summary: %s", exc)
        return _demo_debrief(case_packet, session) + f"\n\n> _Note: Live Evaluator API call failed ({exc}); generated local telemetry fallback._\n"
