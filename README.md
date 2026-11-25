# Voice-First Product Sense Interview Harness (Phase 1)

A local, voice-first **45-minute Product Sense interview simulator** built from [docs/product-sense-interview-harness-spec.md](docs/product-sense-interview-harness-spec.md), seeded with two Senior PM — External Developer Experience case studies grounded in [docs/2026-11-24-sokin-senior-pm-external-developer-experience.md](docs/2026-11-24-sokin-senior-pm-external-developer-experience.md).

## What's Included in Phase 1

- **Voice-Only Push-to-Talk (PTT) Frontend (`frontend/` — React + Vite + TypeScript):**
  - Hold `Spacebar` or click **Start Speaking / Done Speaking** (`MediaRecorder` audio capture).
  - Text input is disabled during active interviews to enforce thinking out loud.
  - **45-Minute Countdown Timer & 6-Phase Progress Bar** (`Brief & Clarify` → `Framing & Strategy` → `Deep Dive` → `Curveball` → `Executive Wrap-Up` → `Hard Stop`).
  - **Thinking-Out-Loud Guardrails:** Configurable silence nudge timer (45s / 60s / 90s / Off) + turn-length color indicator (**amber at 2:30**, **red at 3:30**).
  - **Toggleable Interviewer Voice (TTS):** Switch between the default browser Web Speech voice and **ElevenLabs** (when `ELEVENLABS_API_KEY` is set in `.env`), with live text transcript and per-turn replay.
  - **Two-Pane Layout:** Case Brief viewer on the left (with Phase 2 Excalidraw Whiteboard slot) and Interview Console on the right.
- **FastAPI Backend & Agents (`backend/`):**
  - Single-roundtrip **Gemini 2.5 Flash** native audio transcription + active panel interviewer agent (`google-genai`).
  - Deterministic **Phase Controller** & scripted curveball injector.
  - **Post-Session Evaluator Agent** generating scored `debrief.md` reports (Overall Verdict, 5 Dimension Scores, Moment-by-Moment Replay with 30-second Upgrade Answers, and Targeted Drills).
  - **Automatic Demo Mode:** Runs cleanly without an API key so you can test the full workflow immediately; add `GEMINI_API_KEY` in `.env` for live audio transcription and Gemini interviewer/evaluator reasoning.
- **Seeded Sokin Case Packets (`cases/`):**
  1. `sokin-api-vs-mcp-prioritisation.json` — *API Foundation vs. MCP Agentic Treasury Prioritisation*
  2. `sokin-docs-sandbox-ttfp.json` — *Redesigning `docs.sokin.com` & Sandbox for <1-Day First Payment*
- **Persistent Session Archive (`sessions/`):**
  - Every run writes `sessions/YYYY-MM-DD-[company]-[topic]-[id]/` containing `case-packet.json`, `transcript.json`, and `debrief.md`.

## Quick Start

### 1. Configure Environment
```bash
cp .env.example .env
# Add your GEMINI_API_KEY to .env (or leave blank to run in Demo Mode)
```

### 2. Run the Backend (FastAPI on port 8000)
```bash
cd backend
uv sync --extra dev
uv run uvicorn app.main:app --reload --port 8000
```

### 3. Run the Frontend (Vite on port 3000)
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in Chrome, pick a Sokin case packet, and start your 45-minute mock interview.

## Running Backend Tests
```bash
cd backend
uv run pytest
```

## Roadmap
- **Phase 1 (merged):** MVP Voice PTT + 45-min Phase State Machine + Sokin Case Runner + `debrief.md` Evaluator + ElevenLabs TTS toggle.
- **Phase 2 (this branch):** Embedded `@excalidraw/excalidraw` whiteboard in the left pane with turn-synchronized PNG + JSON diff capture, Audio-Only Mode toggle, multimodal Interviewer & Evaluator vision inspection, and Whiteboard Timeline in the Debrief view.
- **Phase 3:** Antigravity Skill / Case Generator Bridge from any `role-prep/*.md` + public API docs.
