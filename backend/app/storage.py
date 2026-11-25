from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models import (
    CandidateCaseView,
    CasePacket,
    CaseSummary,
    SessionState,
    SessionSummary,
)
from app.phase_machine import get_all_phases, get_phase_for_elapsed


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:40] or "case"


class Storage:
    def __init__(self, cases_dir: Optional[Path] = None, sessions_dir: Optional[Path] = None):
        self.cases_dir = cases_dir or settings.cases_dir
        self.sessions_dir = sessions_dir or settings.sessions_dir
        self.cases_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    # --- Case Packets ---

    def list_cases(self) -> list[CaseSummary]:
        summaries: list[CaseSummary] = []
        for path in sorted(self.cases_dir.glob("*.json")):
            packet = CasePacket.model_validate_json(path.read_text(encoding="utf-8"))
            summaries.append(
                CaseSummary(
                    id=packet.id,
                    title=packet.title,
                    company=packet.company,
                    role=packet.role,
                    duration_minutes=packet.duration_minutes,
                    difficulty=packet.difficulty,
                    tags=packet.tags,
                    interviewers=packet.interviewers,
                    evaluation_focus=packet.evaluation_focus,
                )
            )
        return summaries

    def get_case(self, case_id: str) -> Optional[CasePacket]:
        for path in self.cases_dir.glob("*.json"):
            packet = CasePacket.model_validate_json(path.read_text(encoding="utf-8"))
            if packet.id == case_id:
                return packet
        return None

    def get_candidate_case_view(self, case_id: str) -> Optional[CandidateCaseView]:
        packet = self.get_case(case_id)
        if not packet:
            return None
        return CandidateCaseView(
            id=packet.id,
            title=packet.title,
            company=packet.company,
            role=packet.role,
            duration_minutes=packet.duration_minutes,
            difficulty=packet.difficulty,
            tags=packet.tags,
            interviewers=packet.interviewers,
            evaluation_focus=packet.evaluation_focus,
            candidate_brief_markdown=packet.candidate_brief_markdown,
        )

    # --- Sessions ---

    def _session_dir(self, session_id: str) -> Path:
        return self.sessions_dir / session_id

    def create_session(
        self,
        case_packet: CasePacket,
        reading_grace_seconds: int = 120,
        silence_nudge_seconds: int = 60,
        tts_enabled: bool = True,
        tts_provider: str = "browser",
        demo_mode: bool = False,
    ) -> SessionState:
        now = datetime.now(timezone.utc)
        date_prefix = now.strftime("%Y-%m-%d")
        company_slug = _slugify(case_packet.company)
        topic_slug = _slugify(case_packet.id.replace(f"{company_slug}-", ""))
        short_id = uuid.uuid4().hex[:6]
        session_id = f"{date_prefix}-{company_slug}-{topic_slug}-{short_id}"

        sdir = self._session_dir(session_id)
        sdir.mkdir(parents=True, exist_ok=True)
        (sdir / "case-packet.json").write_text(
            case_packet.model_dump_json(indent=2),
            encoding="utf-8",
        )

        phases = get_all_phases(case_packet.duration_minutes)
        current_phase = get_phase_for_elapsed(0, case_packet.duration_minutes)

        session = SessionState(
            session_id=session_id,
            case_id=case_packet.id,
            title=case_packet.title,
            company=case_packet.company,
            role=case_packet.role,
            started_at=now,
            status="active",
            duration_minutes=case_packet.duration_minutes,
            reading_grace_seconds=reading_grace_seconds,
            silence_nudge_seconds=silence_nudge_seconds,
            tts_enabled=tts_enabled,
            tts_provider=tts_provider,  # type: ignore[arg-type]
            demo_mode=demo_mode,
            current_phase=current_phase,
            phases=phases,
            elapsed_seconds=0,
            curveballs_injected=[],
            interviewers=case_packet.interviewers,
            candidate_brief_markdown=case_packet.candidate_brief_markdown,
            turns=[],
        )
        self.save_session(session)
        return session

    def save_session(self, session: SessionState) -> None:
        sdir = self._session_dir(session.session_id)
        sdir.mkdir(parents=True, exist_ok=True)

        # Persist transcript.json (complete session state & turns)
        (sdir / "transcript.json").write_text(
            session.model_dump_json(indent=2),
            encoding="utf-8",
        )

        # Persist debrief.md when available
        if session.debrief_markdown:
            (sdir / "debrief.md").write_text(
                session.debrief_markdown,
                encoding="utf-8",
            )

    def get_session(self, session_id: str) -> Optional[SessionState]:
        transcript_path = self._session_dir(session_id) / "transcript.json"
        if not transcript_path.exists():
            return None
        session = SessionState.model_validate_json(transcript_path.read_text(encoding="utf-8"))
        debrief_path = self._session_dir(session_id) / "debrief.md"
        if debrief_path.exists() and not session.debrief_markdown:
            session.debrief_markdown = debrief_path.read_text(encoding="utf-8")
        return session

    def get_session_case_packet(self, session_id: str) -> Optional[CasePacket]:
        case_path = self._session_dir(session_id) / "case-packet.json"
        if not case_path.exists():
            return None
        return CasePacket.model_validate_json(case_path.read_text(encoding="utf-8"))

    def list_sessions(self) -> list[SessionSummary]:
        summaries: list[SessionSummary] = []
        if not self.sessions_dir.exists():
            return summaries
        for sdir in sorted(self.sessions_dir.iterdir(), reverse=True):
            if not sdir.is_dir():
                continue
            transcript_path = sdir / "transcript.json"
            if not transcript_path.exists():
                continue
            try:
                raw = json.loads(transcript_path.read_text(encoding="utf-8"))
                has_debrief = (sdir / "debrief.md").exists() or bool(raw.get("debrief_markdown"))
                summaries.append(
                    SessionSummary(
                        session_id=raw["session_id"],
                        case_id=raw["case_id"],
                        title=raw["title"],
                        company=raw["company"],
                        role=raw["role"],
                        started_at=raw["started_at"],
                        ended_at=raw.get("ended_at"),
                        status=raw["status"],
                        elapsed_seconds=raw.get("elapsed_seconds", 0),
                        turn_count=len(raw.get("turns", [])),
                        has_debrief=has_debrief,
                        demo_mode=raw.get("demo_mode", False),
                    )
                )
            except Exception:
                continue
        return summaries
