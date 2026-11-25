import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app import case_generator, main
from app.config import PROJECT_ROOT, settings
from app.models import CasePacket
from app.storage import Storage


def test_generate_case_api_endpoint(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "")
    cases_dir = tmp_path / "cases"
    test_storage = Storage(cases_dir=cases_dir, sessions_dir=tmp_path / "sessions")
    monkeypatch.setattr(main, "storage", test_storage)

    async def fake_fetch(url: str, max_chars: int = 10000):
        return f"Mock API docs content for {url}: OAuth2, Payments API, Webhooks.", None

    monkeypatch.setattr(case_generator, "fetch_url_text", fake_fetch)

    client = TestClient(main.app)

    # Empty payload -> 400
    bad = client.post("/api/cases/generate", json={"source_markdown": "", "urls": []})
    assert bad.status_code == 400

    # Valid payload -> saves JSON to cases/ and returns CaseSummary
    res = client.post(
        "/api/cases/generate",
        json={
            "source_markdown": "# Role Prep: Senior PM — External Developer Experience — Sokin\n\nSokin operates in 36 licensed countries.",
            "urls": ["https://docs.sokin.com/"],
            "topic": "White-Label KYB SLA Parity",
            "company": "Sokin",
            "role": "Senior PM — External Developer Experience",
            "duration_minutes": 45,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["used_demo_mode"] is True
    assert body["case"]["company"] == "Sokin"
    assert body["case"]["title"] == "White-Label KYB SLA Parity"

    saved_path = cases_dir / f"{body['case']['id']}.json"
    assert saved_path.exists()
    loaded = CasePacket.model_validate_json(saved_path.read_text(encoding="utf-8"))
    assert len(loaded.hidden_facts) >= 4
    assert len(loaded.curveballs) >= 2
    assert "docs.sokin.com" in loaded.candidate_brief_markdown

    # Newly generated case is immediately returned by GET /api/cases
    listed = client.get("/api/cases").json()
    assert any(c["id"] == body["case"]["id"] for c in listed)


def test_cli_validate_and_generate(tmp_path: Path):
    script = PROJECT_ROOT / "scripts" / "generate_case.py"

    # 1. Validate an existing seeded Sokin case
    val_proc = subprocess.run(
        [sys.executable, str(script), "--validate-only", "cases/sokin-api-vs-mcp-prioritisation.json"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert val_proc.returncode == 0, val_proc.stderr
    assert "VALID: sokin-api-vs-mcp-prioritisation" in val_proc.stdout

    # 2. Generate a new case from the Sokin role-prep doc in Demo Mode (empty GEMINI_API_KEY)
    out_file = tmp_path / "generated-case.json"
    env = {"PATH": "", "GEMINI_API_KEY": ""}
    gen_proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--source",
            "docs/2026-11-24-sokin-senior-pm-external-developer-experience.md",
            "--topic",
            "Embedded Finance Partner Kit",
            "--output",
            str(out_file),
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert gen_proc.returncode == 0, gen_proc.stderr
    assert out_file.exists()
    packet = CasePacket.model_validate_json(out_file.read_text(encoding="utf-8"))
    assert packet.company == "Sokin"
    assert packet.title == "Embedded Finance Partner Kit"
