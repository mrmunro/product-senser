from pathlib import Path

from fastapi.testclient import TestClient

from app import main
from app.config import settings
from app.models import PhaseId
from app.phase_machine import get_phase_for_elapsed, should_inject_curveball
from app.storage import Storage


def test_phase_machine_windows():
    assert get_phase_for_elapsed(0).id == PhaseId.BRIEF_CLARIFY
    assert get_phase_for_elapsed(5 * 60 + 59).id == PhaseId.BRIEF_CLARIFY
    assert get_phase_for_elapsed(6 * 60).id == PhaseId.FRAMING_STRATEGY
    assert get_phase_for_elapsed(13 * 60).id == PhaseId.DEEP_DIVE
    assert get_phase_for_elapsed(28 * 60).id == PhaseId.CURVEBALL
    assert get_phase_for_elapsed(38 * 60).id == PhaseId.EXECUTIVE_WRAPUP
    assert get_phase_for_elapsed(43 * 60).id == PhaseId.HARD_STOP
    assert get_phase_for_elapsed(50 * 60).id == PhaseId.HARD_STOP


def test_curveball_injection_schedule():
    deep_dive = get_phase_for_elapsed(20 * 60)
    assert should_inject_curveball(deep_dive, [], 2, 20 * 60) is None

    curveball_start = get_phase_for_elapsed(28 * 60 + 10)
    assert should_inject_curveball(curveball_start, [], 2, 28 * 60 + 10) == 0
    assert should_inject_curveball(curveball_start, [0], 2, 29 * 60) is None
    assert should_inject_curveball(curveball_start, [0], 2, 33 * 60 + 5) == 1
    assert should_inject_curveball(curveball_start, [0, 1], 2, 36 * 60) is None


def test_end_to_end_session_lifecycle(tmp_path: Path, monkeypatch):
    # Force Demo Mode and isolate sessions directory to tmp_path
    monkeypatch.setattr(settings, "gemini_api_key", "")
    test_storage = Storage(cases_dir=settings.cases_dir, sessions_dir=tmp_path / "sessions")
    monkeypatch.setattr(main, "storage", test_storage)

    client = TestClient(main.app)

    # 1. Health check reports demo mode
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["demo_mode"] is True

    # 2. Seeded Sokin cases load properly and hide hidden_facts from candidate view
    cases_res = client.get("/api/cases")
    assert cases_res.status_code == 200
    case_ids = {c["id"] for c in cases_res.json()}
    assert "sokin-api-vs-mcp-prioritisation" in case_ids
    assert "sokin-docs-sandbox-ttfp" in case_ids

    case_detail = client.get("/api/cases/sokin-api-vs-mcp-prioritisation")
    assert case_detail.status_code == 200
    detail_json = case_detail.json()
    assert "hidden_facts" not in detail_json
    assert "curveballs" not in detail_json
    assert "Sokin" in detail_json["candidate_brief_markdown"]

    # 3. Create session -> has opening interviewer turn
    created = client.post(
        "/api/sessions",
        json={
            "case_id": "sokin-api-vs-mcp-prioritisation",
            "silence_nudge_seconds": 60,
            "tts_enabled": True,
        },
    )
    assert created.status_code == 200
    session = created.json()
    session_id = session["session_id"]
    assert session["status"] == "active"
    assert len(session["turns"]) == 1
    assert session["turns"][0]["role"] == "interviewer"

    # 4. Submit Phase 1 clarifying turn
    turn1 = client.post(
        f"/api/sessions/{session_id}/turn",
        data={
            "elapsed_seconds": "120",
            "speaking_duration_seconds": "42.5",
            "demo_transcript": "Before framing strategy, what is our engineering capacity and squad makeup for the next two quarters?",
        },
    )
    assert turn1.status_code == 200
    t1_json = turn1.json()
    assert t1_json["current_phase"]["id"] == "brief_clarify"
    assert "5 engineers" in t1_json["interviewer_turn"]["text"]

    # 5. Trigger a silence nudge
    nudge = client.post(f"/api/sessions/{session_id}/nudge", json={"elapsed_seconds": "240"})
    assert nudge.status_code == 200
    assert nudge.json()["is_nudge"] is True

    # 6. Submit Phase 4 turn -> injects curveball 0
    turn2 = client.post(
        f"/api/sessions/{session_id}/turn",
        data={
            "elapsed_seconds": str(29 * 60),
            "speaking_duration_seconds": "95.0",
            "demo_transcript": "I'll enforce MCP spend limits and idempotency in the API gateway layer while fixing sandbox drift.",
        },
    )
    assert turn2.status_code == 200
    t2_json = turn2.json()
    assert t2_json["current_phase"]["id"] == "curveball"
    assert t2_json["curveballs_injected"] == [0]
    assert t2_json["interviewer_turn"]["curveball_index"] == 0

    # 7. End session -> generates debrief.md and persists files
    ended = client.post(f"/api/sessions/{session_id}/end", json={"elapsed_seconds": str(40 * 60)})
    assert ended.status_code == 200
    ended_json = ended.json()
    assert ended_json["status"] == "completed"
    assert "Overall Readiness Verdict" in ended_json["debrief_markdown"]

    session_dir = tmp_path / "sessions" / session_id
    assert (session_dir / "case-packet.json").exists()
    assert (session_dir / "transcript.json").exists()
    assert (session_dir / "debrief.md").exists()

    # 8. Sessions list shows completed session with debrief
    sessions_list = client.get("/api/sessions")
    assert sessions_list.status_code == 200
    assert any(s["session_id"] == session_id and s["has_debrief"] for s in sessions_list.json())
