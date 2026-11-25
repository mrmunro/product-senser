import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import main
from app.config import settings
from app.storage import Storage

# Minimal valid 1x1 transparent PNG bytes
FAKE_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_phase2_whiteboard_capture_and_persistence(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "")
    test_storage = Storage(cases_dir=settings.cases_dir, sessions_dir=tmp_path / "sessions")
    monkeypatch.setattr(main, "storage", test_storage)

    client = TestClient(main.app)

    # 1. Start session with whiteboard enabled
    created = client.post(
        "/api/sessions",
        json={
            "case_id": "sokin-api-vs-mcp-prioritisation",
            "silence_nudge_seconds": 60,
            "tts_enabled": True,
            "whiteboard_enabled": True,
        },
    )
    assert created.status_code == 200
    session = created.json()
    session_id = session["session_id"]
    assert session["whiteboard_enabled"] is True

    # 2. Submit Phase 3 turn with PNG snapshot, JSON diff, and Excalidraw scene
    diff_payload = {
        "element_count": 4,
        "added_count": 4,
        "modified_count": 0,
        "removed_count": 0,
        "new_labels": ["Core Gateway", "MCP Entitlements", "Audit Ledger"],
        "all_labels": ["Core Gateway", "MCP Entitlements", "Audit Ledger"],
        "summary": "+4 added (Core Gateway, MCP Entitlements, Audit Ledger) · 4 total",
    }
    scene_json = json.dumps({"type": "excalidraw", "version": 2, "elements": []})

    turn = client.post(
        f"/api/sessions/{session_id}/turn",
        data={
            "elapsed_seconds": str(15 * 60),
            "speaking_duration_seconds": "64.0",
            "demo_transcript": "I placed MCP Entitlements and spend caps inside the Core Gateway layer.",
            "whiteboard_diff": json.dumps(diff_payload),
            "whiteboard_scene": scene_json,
        },
        files={"whiteboard_png": ("whiteboard.png", FAKE_PNG, "image/png")},
    )
    assert turn.status_code == 200
    t_json = turn.json()
    assert t_json["whiteboard_snapshot"] is not None
    snap_filename = t_json["whiteboard_snapshot"]["filename"]
    assert snap_filename.endswith(".png")
    assert t_json["candidate_turn"]["whiteboard_snapshot"] == snap_filename
    assert "Core Gateway" in t_json["interviewer_turn"]["text"]

    # 3. Verify snapshot image & final.excalidraw are served cleanly
    img_res = client.get(f"/api/sessions/{session_id}/snapshots/{snap_filename}")
    assert img_res.status_code == 200
    assert img_res.headers["content-type"] == "image/png"
    assert img_res.content == FAKE_PNG

    scene_res = client.get(f"/api/sessions/{session_id}/snapshots/final.excalidraw")
    assert scene_res.status_code == 200
    assert scene_res.json()["type"] == "excalidraw"

    # 4. Save final whiteboard snapshot before ending session
    final_wb = client.post(
        f"/api/sessions/{session_id}/whiteboard",
        data={
            "elapsed_seconds": str(39 * 60),
            "element_count": "6",
            "whiteboard_scene": scene_json,
        },
        files={"whiteboard_png": ("final.png", FAKE_PNG, "image/png")},
    )
    assert final_wb.status_code == 200
    assert final_wb.json()["filename"] == "final.png"

    # 5. End session and verify debrief references whiteboard snapshots
    ended = client.post(f"/api/sessions/{session_id}/end", json={"elapsed_seconds": str(40 * 60)})
    assert ended.status_code == 200
    ended_json = ended.json()
    assert ended_json["has_final_excalidraw"] is True
    assert len(ended_json["whiteboard_snapshots"]) == 2
    assert "Whiteboard Effectiveness" in ended_json["debrief_markdown"]
    assert "2 Excalidraw snapshot(s) captured" in ended_json["debrief_markdown"]
