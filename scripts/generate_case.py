#!/usr/bin/env python3
"""One-command CLI bridge to generate or validate a Case Packet JSON for the Interview Harness.

Examples:
  uv run --directory backend python ../scripts/generate_case.py \\
    --source docs/2026-11-24-sokin-senior-pm-external-developer-experience.md \\
    --url https://docs.sokin.com/ \\
    --topic "White-Label Partner Onboarding & KYB SLA Parity"

  uv run --directory backend python ../scripts/generate_case.py \\
    --validate-only cases/sokin-api-vs-mcp-prioritisation.json
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.case_generator import generate_case_packet  # noqa: E402
from app.models import CasePacket  # noqa: E402


def _read_sources(paths: list[str]) -> str:
    sections: list[str] = []
    for raw in paths:
        p = Path(raw)
        if not p.is_absolute():
            p = (PROJECT_ROOT / raw).resolve() if (PROJECT_ROOT / raw).exists() else p.resolve()
        if not p.exists():
            raise FileNotFoundError(f"Source file not found: {raw}")
        content = p.read_text(encoding="utf-8")
        sections.append(f"<!-- Source: {p.name} -->\n{content}")
    return "\n\n---\n\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate or validate a Product Sense Case Packet JSON.",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Path to a role-prep Markdown file, JD, or proposal (repeatable).",
    )
    parser.add_argument(
        "--url",
        action="append",
        default=[],
        help="Public documentation URL to include (e.g. https://docs.sokin.com/) (repeatable).",
    )
    parser.add_argument("--topic", default=None, help="Specific case focus or dilemma to centre the case around.")
    parser.add_argument("--company", default=None, help="Optional company name override.")
    parser.add_argument("--role", default=None, help="Optional role title override.")
    parser.add_argument("--duration", type=int, default=45, help="Interview duration in minutes (default: 45).")
    parser.add_argument("--id", dest="case_id", default=None, help="Optional kebab-case ID override.")
    parser.add_argument("--output", default=None, help="Output JSON path (defaults to cases/<id>.json).")
    parser.add_argument(
        "--validate-only",
        default=None,
        help="Validate an existing case-packet JSON file against the CasePacket schema and exit.",
    )

    args = parser.parse_args()

    if args.validate_only:
        target = Path(args.validate_only)
        if not target.is_absolute() and not target.exists():
            target = PROJECT_ROOT / args.validate_only
        packet = CasePacket.model_validate_json(target.read_text(encoding="utf-8"))
        print(
            f"VALID: {packet.id} — {packet.title} ({packet.company}, "
            f"{len(packet.hidden_facts)} hidden facts, {len(packet.curveballs)} curveballs)"
        )
        return 0

    if not args.source and not args.url:
        parser.error("Provide at least one --source file or --url (or use --validate-only).")

    source_md = _read_sources(args.source) if args.source else ""
    result = asyncio.run(
        generate_case_packet(
            source_markdown=source_md,
            urls=args.url,
            topic=args.topic,
            company=args.company,
            role=args.role,
            duration_minutes=args.duration,
            case_id=args.case_id,
        )
    )

    packet = result.case_packet
    out_path = Path(args.output) if args.output else PROJECT_ROOT / "cases" / f"{packet.id}.json"
    if not out_path.is_absolute():
        out_path = PROJECT_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(packet.model_dump_json(indent=2) + "\n", encoding="utf-8")

    mode_label = "Demo Mode" if result.used_demo_mode else "Gemini"
    print(f"Generated Case Packet ({mode_label}): {out_path}")
    print(f"  ID:           {packet.id}")
    print(f"  Title:        {packet.title}")
    print(f"  Company/Role: {packet.company} — {packet.role}")
    print(f"  Hidden facts: {len(packet.hidden_facts)} | Curveballs: {len(packet.curveballs)}")
    for warning in result.warnings:
        print(f"  [warn] {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
