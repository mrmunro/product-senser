from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class PhaseId(str, Enum):
    BRIEF_CLARIFY = "brief_clarify"
    FRAMING_STRATEGY = "framing_strategy"
    DEEP_DIVE = "deep_dive"
    CURVEBALL = "curveball"
    EXECUTIVE_WRAPUP = "executive_wrapup"
    HARD_STOP = "hard_stop"


class PhaseInfo(BaseModel):
    id: PhaseId
    number: int
    name: str
    start_minute: float
    end_minute: float
    objective: str
    interviewer_behavior: str


class InterviewerPersona(BaseModel):
    name: str
    role: str
    focus: str


class CasePacket(BaseModel):
    id: str
    title: str
    company: str
    role: str
    duration_minutes: int = 45
    difficulty: str = "Senior PM"
    tags: list[str] = Field(default_factory=list)
    interviewers: list[InterviewerPersona]
    candidate_brief_markdown: str
    hidden_facts: dict[str, str] = Field(default_factory=dict)
    curveballs: list[str] = Field(default_factory=list)
    evaluation_focus: list[str] = Field(default_factory=list)


class CaseSummary(BaseModel):
    id: str
    title: str
    company: str
    role: str
    duration_minutes: int
    difficulty: str
    tags: list[str]
    interviewers: list[InterviewerPersona]
    evaluation_focus: list[str]


class CandidateCaseView(CaseSummary):
    """Candidate-safe view of a CasePacket (omits hidden_facts and scripted curveballs)."""

    candidate_brief_markdown: str


class WhiteboardSnapshotMeta(BaseModel):
    filename: str
    turn_id: Optional[str] = None
    phase: PhaseId
    elapsed_seconds: int
    element_count: int = 0
    diff_summary: Optional[str] = None
    timestamp: datetime


class TranscriptTurn(BaseModel):
    id: str
    role: Literal["candidate", "interviewer", "system"]
    speaker_name: str
    speaker_role: str = ""
    text: str
    phase: PhaseId
    elapsed_seconds: int
    speaking_duration_seconds: float = 0.0
    timestamp: datetime
    is_nudge: bool = False
    curveball_index: Optional[int] = None
    delivery_notes: Optional[str] = None
    whiteboard_snapshot: Optional[str] = None
    whiteboard_diff_summary: Optional[str] = None


class SessionState(BaseModel):
    session_id: str
    case_id: str
    title: str
    company: str
    role: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: Literal["active", "completed"] = "active"
    duration_minutes: int = 45
    reading_grace_seconds: int = 120
    silence_nudge_seconds: int = 60
    tts_enabled: bool = True
    tts_provider: Literal["browser", "elevenlabs"] = "browser"
    whiteboard_enabled: bool = True
    demo_mode: bool = False
    current_phase: PhaseInfo
    phases: list[PhaseInfo]
    elapsed_seconds: int = 0
    curveballs_injected: list[int] = Field(default_factory=list)
    interviewers: list[InterviewerPersona] = Field(default_factory=list)
    candidate_brief_markdown: str = ""
    turns: list[TranscriptTurn] = Field(default_factory=list)
    whiteboard_snapshots: list[WhiteboardSnapshotMeta] = Field(default_factory=list)
    has_final_excalidraw: bool = False
    debrief_markdown: Optional[str] = None


class SessionSummary(BaseModel):
    session_id: str
    case_id: str
    title: str
    company: str
    role: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: Literal["active", "completed"]
    elapsed_seconds: int
    turn_count: int
    has_debrief: bool
    demo_mode: bool


class CreateSessionRequest(BaseModel):
    case_id: str
    reading_grace_seconds: int = Field(default=120, ge=0, le=600)
    silence_nudge_seconds: int = Field(default=60, ge=0, le=300)
    tts_enabled: bool = True
    tts_provider: Literal["browser", "elevenlabs"] = "browser"
    whiteboard_enabled: bool = True


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=3000)
    voice_id: Optional[str] = None


class GenerateCaseRequest(BaseModel):
    source_markdown: str = Field(default="", max_length=120000)
    urls: list[str] = Field(default_factory=list)
    topic: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    duration_minutes: int = Field(default=45, ge=15, le=90)
    case_id: Optional[str] = None


class GenerateCaseResponse(BaseModel):
    case: CaseSummary
    warnings: list[str] = Field(default_factory=list)
    used_demo_mode: bool = False


class NudgeRequest(BaseModel):
    elapsed_seconds: int = Field(ge=0)


class EndSessionRequest(BaseModel):
    elapsed_seconds: int = Field(ge=0)


class TurnResponse(BaseModel):
    candidate_turn: TranscriptTurn
    interviewer_turn: TranscriptTurn
    current_phase: PhaseInfo
    elapsed_seconds: int
    curveballs_injected: list[int]
    whiteboard_snapshot: Optional[WhiteboardSnapshotMeta] = None
    should_hard_stop: bool = False
