# Voice-First Product Sense Interview Harness

A local, voice-first **45-minute Product Sense & Architecture interview simulator** with an embedded **Excalidraw whiteboard**, active multimodal AI panel interviewers, deterministic phase pacing, and scored post-session debriefs.

Built from [docs/product-sense-interview-harness-spec.md](docs/product-sense-interview-harness-spec.md) and seeded with two Senior PM (External Developer Experience) case studies grounded in [docs/2026-11-24-sokin-senior-pm-external-developer-experience.md](docs/2026-11-24-sokin-senior-pm-external-developer-experience.md).

---

## Key Features

- **Voice-Only Push-to-Talk (PTT):** Hold `Spacebar` or click **Start Speaking / Done Speaking** (`MediaRecorder` audio capture). Typing is disabled during active interviews to build the thinking-out-loud reflex.
- **Embedded Excalidraw Whiteboard (Multimodal Vision):** Draw architectures, flows, and trade-off matrices in the left pane. On every Push-to-Talk submit, the frontend automatically captures a PNG snapshot + JSON diff and sends it alongside your spoken audio so the Interviewer Agent can inspect and critique your diagram live. Includes a 1-click **Core vs. Application Layer Starter Frame** and an **Audio-Only Mode** toggle.
- **45-Minute 6-Phase State Machine:** Deterministic pacing across `Brief & Clarify (0–6m)` → `Framing & Strategy (6–13m)` → `Deep Dive & Architecture (13–28m)` → `Curveball & Pushback (28–38m)` → `Executive Wrap-Up (38–43m)` → `Hard Stop & Debrief (43–45m)`.
- **Thinking-Out-Loud Guardrails:**
  - **2-Minute Reading Grace Period** at the start of every session so you can read the brief before the silence timer activates.
  - Configurable **Silence Nudge** (45s / 60s / 90s / Off) that gently prompts you to narrate what you are weighing.
  - **Turn-Length Indicator** that turns **amber at 2:30** and **red at 3:30** to train concise, structured answers.
- **Dual TTS Voice Engine:** Toggle between the built-in **Browser Voice** (zero config) and **ElevenLabs** (when `ELEVENLABS_API_KEY` is configured), with automatic fallback and per-turn replay.
- **Scored Post-Session Debrief (`debrief.md`):** Multimodal Evaluator Agent reviews your full transcript, timing telemetry, and milestone whiteboard PNGs to produce an Overall Readiness Verdict, 5 Dimension Scores (1–5), Moment-by-Moment Replay with 30-second Upgrade Answers, Targeted Drills, and a **Whiteboard Timeline** with `.excalidraw` download.
- **Reusable Case Generator:** Turn any role-prep Markdown file, JD, proposal, or public documentation URL into a validated `cases/<id>.json` via the Lobby UI, a one-command CLI, or the built-in Antigravity workspace skill.

---

## Prerequisites

Before installing, make sure you have:

- **Python 3.11+** and **[`uv`](https://docs.astral.sh/uv/)** (Python package manager)
- **Node.js 20+** and **npm**
- **Google Chrome** (or another Chromium/modern browser) with microphone permissions enabled
- **Optional API Keys:**
  - `GEMINI_API_KEY` — Required for live audio transcription, multimodal Excalidraw critique, LLM case generation, and scored debriefs. *(Without it, the app runs in local **Demo Mode** so you can explore the full UI and workflow offline.)*
  - `ELEVENLABS_API_KEY` — Optional; unlocks ElevenLabs TTS voices alongside the default browser voice.

---

## Step-by-Step Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/mrmunro/product-senser.git
cd product-senser
```

### Step 2: Configure Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

| Variable | Required? | Default | Purpose |
|---|---|---|---|
| `GEMINI_API_KEY` | Recommended | *(blank → Demo Mode)* | Enables live Gemini audio STT, multimodal whiteboard vision, AI case generation, and LLM debrief scoring. |
| `GEMINI_INTERVIEWER_MODEL` | No | `gemini-2.5-flash` | Gemini model used for interviewer turns and case generation. |
| `GEMINI_EVALUATOR_MODEL` | No | `gemini-2.5-flash` | Gemini model used for post-session `debrief.md` evaluation. |
| `ELEVENLABS_API_KEY` | No | *(blank)* | Unlocks the **ElevenLabs** voice option in the Lobby and Interview Room. |
| `ELEVENLABS_VOICE_ID` | No | `JBFqnCBsd6RMkjVDRZzb` | ElevenLabs voice ID (defaults to *George*; replace with any voice ID from your account). |
| `ELEVENLABS_MODEL_ID` | No | `eleven_flash_v2_5` | Low-latency ElevenLabs TTS model. |
| `BACKEND_HOST` / `BACKEND_PORT` | No | `127.0.0.1` / `8000` | Local FastAPI bind host and port. |

> **Note:** After editing `.env`, restart the backend server so the new environment variables take effect.

### Step 3: Install Backend Dependencies
```bash
cd backend
uv sync --extra dev
cd ..
```

### Step 4: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## Running the App Locally

Open **two terminal windows** from the repository root:

### Terminal 1 — Start the FastAPI Backend (port 8000)
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Start the Vite Frontend (port 3000)
```bash
cd frontend
npm run dev
```

Open **http://localhost:3000** in Chrome.
- The badge at the top of the Lobby will show **Live Gemini (`gemini-2.5-flash`)** when `GEMINI_API_KEY` is active, or **Demo Mode** if no key is configured.

---

## Step-by-Step User Guide

### 1. Configure Your Session in the Lobby
1. **Select a Case Packet** (two Sokin Senior PM cases are pre-seeded, or generate your own).
2. **Choose Thinking-Out-Loud Silence Nudge:** `45s`, `60s` (Recommended), `90s`, or `Off`.
3. **Configure Interviewer Voice (TTS):** Toggle Voice On/Off, and if `ELEVENLABS_API_KEY` is set, switch between **Browser (Default)** and **ElevenLabs**.
4. **Choose Interview Mode:** **Voice + Whiteboard** (default) or **Audio-Only Mode**.
5. Click **Start 45-Min Voice Interview**.

### 2. Read the Brief (2-Minute Grace Period)
- When the interview opens, the **Case Brief** tab shows only the business background and the core challenge.
- You get a **2-minute Reading Time** countdown before the silence nudge starts. Start speaking early whenever you are ready.

### 3. Speak & Whiteboard Together
- **Speak:** Hold `Spacebar` (release when finished) or click **Start Speaking** / **Done Speaking**.
  - Pressing `Spacebar` while typing labels inside an Excalidraw text box types a normal space and will not trigger the mic.
  - Keep turns crisp: the recording timer turns **amber at 2:30** and **red at 3:30**.
- **Draw:** Switch to the **Whiteboard** tab in the left pane to sketch architecture or trade-offs (use **Starter Frame** for a quick *Application/DX Layer* vs. *Core Platform/Gateway Layer* layout). Your canvas stays mounted when switching back to the Case Brief.
- **Turn-Sync Capture:** Every time you finish speaking, your current whiteboard PNG and element diff are automatically attached to your turn so the panel can reference what you drew.
- **Hidden Facts & Curveballs:** Ask targeted clarifying questions in Phase 1 to uncover hidden constraints. Expect 1–2 realistic stakeholder curveballs in Phase 4 (`28–38m`).

### 4. Review Your Post-Session Debrief
- At `45:00` (or whenever you click **End & Debrief**), the final whiteboard state is saved and the Evaluator Agent generates `debrief.md`.
- Inspect three tabs:
  1. **Scored Debrief** (with **Copy Markdown** and **Download debrief.md** buttons)
  2. **Full Transcript** (timestamped turns, speaking durations, delivery notes, and inline whiteboard thumbnails)
  3. **Whiteboard Timeline** (gallery of every captured snapshot + **Download `.excalidraw`**)
- Past sessions remain accessible anytime from the **Saved Sessions & Debriefs** sidebar in the Lobby.

---

## Generating Custom Case Packets

You can create new 45-minute cases for any company or PM role in three ways:

### Option 1: From the Lobby UI
1. Click **+ Generate New Case** in the Lobby.
2. Optionally enter a Company, Target Role, Focus Dilemma, and Public Docs URLs (one per line, e.g. `https://docs.sokin.com/`).
3. Paste your role-prep Markdown / JD or click **Load `.md` / `.txt` file**.
4. Click **Generate & Save Case** — it saves directly to `cases/<id>.json` and selects it immediately.

### Option 2: One-Command CLI (`scripts/generate_case.py`)
```bash
uv run --directory backend python ../scripts/generate_case.py \
  --source docs/2026-11-24-sokin-senior-pm-external-developer-experience.md \
  --url https://docs.sokin.com/ \
  --topic "White-Label Partner Onboarding & KYB SLA Parity"
```

Validate any hand-edited or generated case JSON against the schema:
```bash
uv run --directory backend python ../scripts/generate_case.py \
  --validate-only cases/sokin-api-vs-mcp-prioritisation.json
```

### Option 3: Via the Antigravity Workspace Skill
The workspace skill at [.agents/skills/generate-case-packet/SKILL.md](.agents/skills/generate-case-packet/SKILL.md) is automatically discovered by Antigravity. Reference any role-prep file, JD, or URL in chat and ask Antigravity to generate a new case packet — it will author and validate `cases/<id>.json` directly.

---

## Project Structure

```text
.
├── .agents/skills/generate-case-packet/   # Auto-discovered Antigravity skill
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── interviewer.py             # Multimodal audio + whiteboard Interviewer Agent
│   │   │   └── evaluator.py               # Multimodal post-session Evaluator Agent
│   │   ├── case_generator.py              # URL fetcher + Case Packet synthesizer
│   │   ├── config.py                      # .env settings & feature flags
│   │   ├── main.py                        # FastAPI routes
│   │   ├── models.py                      # Pydantic schemas
│   │   ├── phase_machine.py               # 45-min 6-phase state machine & curveballs
│   │   ├── storage.py                     # Case & session file persistence
│   │   └── tts.py                         # ElevenLabs REST TTS client
│   └── tests/                             # Pytest suites (Phases 1–3)
├── cases/                                 # Reusable Case Packet JSON library
├── docs/                                  # Technical spec & Sokin role-prep source doc
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Lobby.tsx                  # Case picker, settings, generator modal, session archive
│       │   ├── InterviewRoom.tsx          # 2-pane voice + whiteboard interview console
│       │   ├── WhiteboardPane.tsx         # Embedded Excalidraw + PNG/diff/scene capture
│       │   └── DebriefView.tsx            # Scored debrief, transcript archive, whiteboard timeline
│       └── hooks/
│           ├── usePushToTalk.ts           # MediaRecorder + Spacebar PTT + turn timer
│           └── useTTS.ts                  # Browser Web Speech & ElevenLabs playback
├── scripts/generate_case.py               # One-command CLI generator & validator
└── sessions/                              # Saved local runs (gitignored):
    └── YYYY-MM-DD-[company]-[topic]-[id]/
        ├── case-packet.json
        ├── transcript.json
        ├── debrief.md
        └── whiteboard-snapshots/
            ├── turn-01-XXmXXs.png
            ├── final.png
            └── final.excalidraw
```

---

## Development & Testing

Run the full backend test suite:
```bash
cd backend
uv run pytest -v
```

Type-check and build the frontend production bundle:
```bash
cd frontend
npm run build
```

### Troubleshooting
- **Microphone not working:** Ensure Chrome has microphone permission for `http://localhost:3000` (check the lock/tune icon in the address bar and macOS System Settings → Privacy & Security → Microphone).
- **Demo Mode vs. Live Mode:** If the Lobby shows *Demo Mode* after adding `GEMINI_API_KEY`, verify `.env` is in the repository root (next to `.env.example`) and restart `uvicorn`.
- **ElevenLabs button disabled:** Add `ELEVENLABS_API_KEY` to `.env`, restart the backend, and refresh `http://localhost:3000`.
