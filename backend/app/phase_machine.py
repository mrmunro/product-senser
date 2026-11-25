from __future__ import annotations

from typing import Optional

from app.models import PhaseId, PhaseInfo


# Base 45-minute phase windows matching Section 4 of the technical spec
_BASE_PHASES: list[tuple[PhaseId, int, str, float, float, str, str]] = [
    (
        PhaseId.BRIEF_CLARIFY,
        1,
        "Brief & Clarify",
        0.0,
        6.0,
        "Read/review case prompt and ask targeted clarifying questions.",
        "Answer clarifying questions strictly from hidden_facts (do not volunteer unasked info). Flag gently if the candidate jumps straight into solutions without clarifying constraints.",
    ),
    (
        PhaseId.FRAMING_STRATEGY,
        2,
        "Framing & Strategy",
        6.0,
        13.0,
        "Define strategic goal, user/relationship segments, and constraints.",
        "Probe 'Why now?', 'Who are we optimising for?', and 'What are we explicitly NOT solving?'. Avoid forcing rigid formulas unless organically relevant.",
    ),
    (
        PhaseId.DEEP_DIVE,
        3,
        "Deep Dive & Architecture",
        13.0,
        28.0,
        "Prioritise trade-offs, separate Core Platform vs. Application/DX layer, and embed Trust-by-Design.",
        "Challenge vague leaps ('Walk me through how you got from A to B'). Probe missing risks: compliance, engineering capacity, support load, gateway enforcement, and sandbox parity.",
    ),
    (
        PhaseId.CURVEBALL,
        4,
        "Curveball & Pushback",
        28.0,
        38.0,
        "Handle realistic stakeholder conflict and re-prioritise under pressure.",
        "Inject scripted curveballs from the case packet and test whether the candidate holds their strategic spine while adapting pragmatically.",
    ),
    (
        PhaseId.EXECUTIVE_WRAPUP,
        5,
        "Executive Wrap-Up",
        38.0,
        43.0,
        "Synthesise final recommendation, sequencing, and success metrics.",
        "Ask for a crisp 2-minute executive pitch to the CPO/CEO covering recommendation, trade-offs, sequencing, and key metrics.",
    ),
    (
        PhaseId.HARD_STOP,
        6,
        "Hard Stop & Debrief",
        43.0,
        45.0,
        "Session ends; lock mic and generate scored debrief.",
        "Wrap up professionally, thank the candidate, and hand off to the Evaluator Agent.",
    ),
]


def get_all_phases(duration_minutes: int = 45) -> list[PhaseInfo]:
    scale = duration_minutes / 45.0
    phases: list[PhaseInfo] = []
    for phase_id, num, name, start_m, end_m, objective, behavior in _BASE_PHASES:
        phases.append(
            PhaseInfo(
                id=phase_id,
                number=num,
                name=name,
                start_minute=round(start_m * scale, 2),
                end_minute=round(end_m * scale, 2),
                objective=objective,
                interviewer_behavior=behavior,
            )
        )
    return phases


def get_phase_for_elapsed(elapsed_seconds: int, duration_minutes: int = 45) -> PhaseInfo:
    elapsed_minutes = max(0.0, elapsed_seconds / 60.0)
    phases = get_all_phases(duration_minutes)
    for phase in phases:
        if elapsed_minutes < phase.end_minute:
            return phase
    return phases[-1]


def should_inject_curveball(
    phase: PhaseInfo,
    curveballs_injected: list[int],
    total_curveballs: int,
    elapsed_seconds: int,
    duration_minutes: int = 45,
) -> Optional[int]:
    """Deterministically decide whether to inject the next scripted curveball."""
    if total_curveballs <= 0 or phase.id != PhaseId.CURVEBALL:
        return None
    if len(curveballs_injected) >= total_curveballs:
        return None

    next_index = len(curveballs_injected)
    if next_index == 0:
        # Inject first curveball as soon as we enter the Curveball phase
        return 0

    # Inject subsequent curveballs spaced evenly across the Curveball window
    phase_span_seconds = max(1.0, (phase.end_minute - phase.start_minute) * 60.0)
    elapsed_in_phase = max(0.0, elapsed_seconds - phase.start_minute * 60.0)
    threshold = (phase_span_seconds / total_curveballs) * next_index
    if elapsed_in_phase >= threshold:
        return next_index

    return None
