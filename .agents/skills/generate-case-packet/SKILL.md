---
name: generate-case-packet
description: >-
  Turns any role-prep Markdown file, job description, proposal, and/or public documentation URL
  (e.g., https://docs.sokin.com/) into a validated Product Sense Interview Harness case-packet.json
  with candidate brief, hidden interviewer facts, panel personas, and stakeholder curveballs.
  Use when the user asks to create, generate, or seed a new mock interview case from prep docs or URLs.
---

# Generate Product Sense Case Packet

Use this skill to generate a realistic, schema-validated `cases/<id>.json` file for the local **Product Sense Interview Harness**.

## Option A — One-Command CLI Generation (Fastest)

Run the built-in CLI bridge from the repository root:

```bash
uv run --directory backend python ../scripts/generate_case.py \
  --source docs/<role-prep-file>.md \
  --url https://docs.example.com/ \
  --topic "<specific product/architecture dilemma>"
```

Flags:
- `--source <path>` (repeatable): Role prep `.md`, JD, or proposal files.
- `--url <url>` (repeatable): Public API docs, changelog, or product pages to index.
- `--topic "<text>"`: Focus dilemma (optional — if omitted, the generator selects the highest-leverage trade-off).
- `--company "<name>"` / `--role "<title>"` / `--duration 45` / `--id <kebab-slug>` / `--output <path>`: Optional overrides.

## Option B — Agent-Authored High-Signal Case Packet

When the user wants extra depth (e.g. combining multiple `career-catalyst-os` prep docs + web research via `search_web`):

1. Read the user's source Markdown files and inspect any public docs URLs.
2. Author `cases/<company>-<short-topic>.json` following the `CasePacket` schema in `backend/app/models.py`:
   - `candidate_brief_markdown`: **Business context + product/technical landscape + specific challenge/decision needed ONLY.** Do **not** include exercise-format instructions (reading time, clarifying-question reminders, or 2-minute wrap-up rules — the Lobby displays those).
   - `interviewers`: 2 complementary personas (typically Group PM / VP Product + Principal Engineer / Architect).
   - `hidden_facts`: 5–7 concrete constraints (squad capacity, current system debt, commercial pipeline, compliance/security stance, baseline metrics) that the Interviewer Agent reveals only when asked.
   - `curveballs`: 2 sharp Phase-4 stakeholder pushbacks.
   - `evaluation_focus`: 4–5 role-specific grading criteria.
3. Validate the file against the Pydantic schema before finishing:

```bash
uv run --directory backend python ../scripts/generate_case.py --validate-only cases/<id>.json
```

## After Generation

Tell the user the saved file path (`cases/<id>.json`) and remind them that it appears immediately in the Lobby at `http://localhost:3000` (refresh if already open) — do not leak `hidden_facts` or `curveballs` in chat unless the user explicitly asks to review them.
