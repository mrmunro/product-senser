# Proposal & Technical Specification: Voice-First Product Sense Interview Harness

_Status: Proposal & Architecture Spec (Pre-Build)_  
_Target Environment: macOS (Apple Silicon) + Antigravity_  
_Date: 25 November 2026_

---

## 1. Problem Statement & Core Goal

Written interview prep does not replicate the cognitive load of a live Product Sense / Case Study interview. In real senior PM interviews (such as whiteboarding an API vs. MCP prioritisation case from a 4-page brief), candidates fail not from lack of knowledge, but from:
* **Not thinking out loud** (going silent while structuring, then jumping straight to a conclusion).
* **Losing structure under interruption** when an interviewer challenges an assumption or introduces an engineering/commercial constraint.
* **Weak visual anchoring** when trying to explain complex system/product trade-offs on a whiteboard.

### What This Harness Must Do
Build a **≤ 45-minute, voice-first, interactive Product Sense interview simulator** that:
1. Ingests any **Role Prep doc / JD**, **Proposal examples**, and/or a **multi-page Case Study Brief** (e.g., Sokin's API vs. MCP prioritisation, or `docs.sokin.com` DX redesign).
2. **Forces spoken answers** (no typing during the interview) using low-latency **Push-to-Talk (PTT)** mic control — avoiding open two-way audio issues.
3. Pairs voice with a **live interactive Whiteboard (Excalidraw)** that the Interviewer Agent can *actually see and critique* on every turn.
4. Roleplays **active, challenging interviewer(s)** who answer clarifying questions from hidden case facts, push back on hand-waving, and enforce a **strict 45-minute timebox**.
5. Produces a **structured post-interview debrief** scoring response structure, clarity, thinking-out-loud discipline, whiteboard usage, and specific improvement drills.

---

## 2. Solving the Two Hard Technical Problems: Voice & Whiteboard

### A. Push-to-Talk Voice (No Open Two-Way Stream, Low Latency)
Keeping a continuous full-duplex voice stream open causes accidental interruptions, awkward pauses, and high complexity. Instead, use **Turn-Based Push-to-Talk (PTT)**:
* **User controls the mic:** Hold `Spacebar` (or click **Start Speaking / Done Speaking**).
* **Voice-Only Enforcement:** The text input box is **disabled** during the active interview session (only mic + whiteboard are active).
* **Fast Transcription (STT):**
  * *Recommended (Local, Free, ~0.5–1.5s latency on Apple Silicon):* **`mlx-whisper`** (`whisper-large-v3-turbo` or `distil-whisper`) running locally via a lightweight Python/FastAPI backend.
  * *Alternative (Zero local setup):* Browser **MediaRecorder** audio blob sent directly to **Gemini 2.5 Flash** (native audio understanding — also captures tone, pauses, and filler words!) or Deepgram/Whisper API.
* **Interviewer Voice Output (TTS):**
  * Interviewer responds in **both spoken audio** (concise 15–30 sec voice reply via fast TTS like macOS `say` / Kokoro-TTS local / ElevenLabs / OpenAI TTS) **and** a clean text transcript in the side panel so you can re-read a complex constraint without asking them to repeat it.

### B. The Whiteboard Problem: Embedded Excalidraw (No Fragile Screen-Share Needed!)
> *Your question: "Can we somehow do this as a browser screen-share if I was using Excalidraw? How would you monitor that and the conversation? If too difficult, exclude it."*

**Verdict: Completely feasible — and much simpler than screen-sharing!**

Screen-sharing a separate browser tab is fragile (OS permissions, continuous video encoding, high token cost). Instead, **embed the open-source `@excalidraw/excalidraw` React component directly inside the harness UI**:

1. **Zero Screen-Share Overhead:** The harness is a single local browser window (`localhost:3000`) split into two panes:
   * **Left Pane (65% width):** Full interactive **Excalidraw** whiteboard (pre-loaded with optional starter frames or blank canvas).
   * **Right Pane (35% width):** 45-min countdown timer + phase indicator, Case Brief viewer (collapsible drawer), Push-to-Talk mic button, and Interviewer conversation log.
2. **Turn-Synchronized Canvas Capture:** Every time you finish speaking and release Push-to-Talk, the frontend automatically runs two built-in Excalidraw API calls (`<100ms`):
   * `exportToBlob()` → captures a crisp **PNG snapshot** of your current whiteboard.
   * `getSceneElements()` → extracts a **lightweight JSON diff** of what you added/changed since the last turn (text boxes, arrows, groupings).
3. **Multimodal Interviewer Turn:** The backend sends `{ spoken_transcript, whiteboard_png, whiteboard_diff, current_phase, elapsed_minutes }` to the Interviewer LLM in a **single request**.
4. **Result:** The interviewer literally sees what you just drew *while* you explained it — and can say:
   > *"I see you put MCP Entitlements in the Application Layer on your diagram — push back on that for me: if an LLM loops and retries a payout, shouldn't the spend cap live in the Core Gateway layer instead?"*

*(Fallback option: If you ever want to run an audio-only drill without drawing, a simple toggle switches to "Audio-Only Mode".)*

---

## 3. Recommended System Architecture (Antigravity + Local Harness)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ANTIGRAVITY (Workspace Orchestrator)                 │
│  1. Reads role-prep/*.md, JD, proposals, API docs (e.g. docs.sokin.com) │
│  2. Generates a structured Case Packet (JSON/MD):                       │
│     • Candidate Brief (1–4 pages)                                       │
│     • Hidden Interviewer Facts & Constraints (answers to Qs)            │
│     • Interviewer Personas & Curveballs                                 │
│  3. Launches local harness & reviews saved post-session debriefs        │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ reads/writes session files
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│             LOCAL INTERVIEW HARNESS (localhost:3000)                    │
│  ┌─────────────────────────────────┬─────────────────────────────────┐  │
│  │  LEFT PANE: Embedded Excalidraw │  RIGHT PANE: Interview Console  │  │
│  │  • Freehand / boxes / arrows    │  • 45:00 Timer & Phase Bar      │  │
│  │  • Auto PNG + JSON snapshot on  │  • Collapsible Case Brief       │  │
│  │    every Push-to-Talk submit    │  • [HOLD SPACE / CLICK] Mic PTT │  │
│  │                                 │  • Interviewer Audio + Text Log │  │
│  └─────────────────────────────────┴─────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ HTTP/WebSocket
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                LOCAL BACKEND (Python FastAPI or Node.js)                │
│  • STT Engine: mlx-whisper (local) or Gemini Flash native audio         │
│  • Interviewer Agent: Gemini 2.5 Pro/Flash (multimodal: text + PNG)     │
│    - Enforces 45-min phase state machine & probing rules                │
│  • TTS Engine: Local Kokoro/Edge-TTS or Cloud TTS                       │
│  • Evaluator Agent (post-session): Generates scored Markdown Debrief    │
└───────────────────────────────┴─────────────────────────────────────────┘
```

### Why This Architecture Wins
* **Clean separation of concerns:** Antigravity handles the heavy research and **Case Packet Generation** (pulling directly from your `career-catalyst-os` prep files and URLs like `docs.sokin.com`). The local web app handles the **real-time Push-to-Talk + Excalidraw UX** cleanly in Chrome without webview mic-permission issues.
* **Persistent Memory:** Every session saves a folder (`sessions/YYYY-MM-DD-[company]-[topic]/`) containing:
  * `case-packet.json` (brief + hidden facts)
  * `transcript.json` (timestamped turns, speaking duration, pauses)
  * `whiteboard-snapshots/` (PNGs at key milestones + final `.excalidraw` file)
  * `debrief.md` (full scored feedback report — readable right inside Antigravity!)

---

## 4. Interview Flow & 45-Minute State Machine

The backend runs a deterministic **Phase Controller** so the interviewer naturally paces the session and never lets it drift past 45 minutes:

| Phase | Time Window | Objective | Interviewer Behaviour |
|---|---|---|---|
| **1. Brief & Clarify** | `00:00 – 06:00` | Read/review case prompt; ask targeted clarifying questions | Answers questions strictly from `hidden_facts` (won't volunteer info you didn't ask for). Flags if you skip clarifying questions and jump straight to solutions. |
| **2. Framing & Strategy** | `06:00 – 13:00` | Define strategic goal, user/relationship segments, and constraints | Probes *"Why now?"*, *"Who are we optimising for?"*, and *"What are we explicitly NOT solving?"* (No forced flywheel formulas unless organically relevant.) |
| **3. Deep Dive & Whiteboard** | `13:00 – 28:00` | Prioritise trade-offs (e.g., API vs. MCP), map Core vs. App layer & Trust-by-Design on Excalidraw | Actively inspects Excalidraw snapshots. Interrupts vague leaps (*"Walk me through how you got from A to B"*). Challenges missing risks (compliance, engineering cost, support load). |
| **4. Curveball / Pushback** | `28:00 – 38:00` | Handle realistic stakeholder conflict | Injects 1–2 scripted curveballs (e.g., *"Engineering says sandbox parity takes 2 quarters; Sales says a £500k partner won't sign without MCP next month — what do you cut?"*). |
| **5. Executive Wrap-Up** | `38:00 – 43:00` | Synthesize final recommendation, sequencing, and key metrics | Asks for a crisp 2-minute pitch to the CPO/CEO. |
| **Hard Stop & Debrief** | `43:00 – 45:00` | Session ends; Evaluator Agent runs | Locks mic, saves final whiteboard PNG, and generates the full scored debrief in ~15 seconds. |

### Anti-Silence & Thinking-Out-Loud Guardrails
Because your stated goal is to build the **thinking-out-loud** reflex:
* **Silence Nudge Timer (Configurable, e.g., 45–60s):** If you haven't pressed Push-to-Talk for 60 seconds while drawing/thinking, a subtle interviewer prompt appears/plays: *"Take a second to narrate what you're weighing right now — even if it's rough."*
* **Turn Length Indicator:** A gentle visual timer on the mic button turns amber at 2:30 and red at 3:30 to train concise, structured spoken turns rather than 6-minute monologues.

---

## 5. Case Packet Input Format (Reusable Across Any Company)

Before starting a session, Antigravity (or a CLI script) generates a `case-packet.json` from any role prep file, JD, or custom document:

```json
{
  "company": "Sokin",
  "role": "Senior PM — External Developer Experience",
  "duration_minutes": 45,
  "interviewers": [
    { "name": "Alex", "role": "Group PM (Get Set Up & Build)", "focus": "Strategy, prioritisation, DX metrics, commercial trade-offs" },
    { "name": "Sam", "role": "Principal Platform Engineer", "focus": "Sandbox parity, API gateway enforcement, MCP security/limits" }
  ],
  "candidate_brief_markdown": "# Case Brief (2–4 pages)...",
  "hidden_facts": {
    "engineering_capacity": "1 squad of 5 engineers for the next 2 quarters; no dedicated tech writer yet.",
    "current_api_state": "Sandbox uses static mocks that drift from production; 40% of support tickets are opaque 400/500 errors.",
    "commercial_pressure": "2 enterprise prospects asking for MCP treasury demos; 1 Tier-1 white-label partner stalled on KYB SLAs."
  },
  "curveballs": [
    "Compliance flags that any autonomous MCP payment execution requires immutable admin audit logs and per-tx caps before GA.",
    "CEO wants an MCP headline at Money20/20 in 8 weeks, while Support is drowning in onboarding tickets."
  ],
  "evaluation_focus": [
    "Thinking out loud before committing",
    "Explicit trade-off framing (API foundation vs. MCP hype)",
    "Core vs. Application architectural clarity",
    "Trust-by-design (compliance/security baked in)"
  ]
}
```

---

## 6. Post-Interview Feedback & Scorecard (`debrief.md`)

After the 45-minute session ends, a dedicated **Evaluator Agent** analyzes the full transcript + every Excalidraw snapshot + timing metadata and outputs:

1. **Overall Readiness Verdict:** Strong Hire / Lean Hire / Needs Drill — with a 3-sentence executive summary.
2. **Dimension Scores (1–5) with Evidence:**
   * **Structure & Signposting:** Did you state your framework upfront (*"I'll cover 3 things: X, Y, Z"*) and keep the interviewer oriented?
   * **Thinking Out Loud:** Did you verbalise trade-offs and hypotheses, or go quiet and jump to conclusions?
   * **Clarity & Conciseness:** Average turn length, rambling/hedging moments, and directness when answering challenges.
   * **Product Sense & Trade-Off Rigor:** Strategic framing, user segmentation, Core vs. App distinction, Trust-by-Design, and realistic prioritisation.
   * **Whiteboard Effectiveness:** Did the Excalidraw diagram reinforce your spoken narrative, or were key concepts left undocumented/messy?
3. **Moment-by-Moment Replay (Top 3–5 Turning Points):**
   * Exact timestamp + quote of what you said (and thumbnail/reference to whiteboard state) → *Why it worked or where it lost the room* → **A concrete 30-second "Upgrade Answer"** showing how to phrase it more crisply.
4. **Targeted Drill for Next Session:** 1–2 focused micro-drills (e.g., *"Next session: 15-minute rapid-fire on handling curveball pushback without abandoning your core thesis"*).

---

## 7. Phased Build Plan (When You Create the New Project)

To get value fast without over-engineering:

* **Phase 1 — MVP Voice + Timer + Case Runner (~1 weekend / 1–2 sessions):**
  * Local React/Vite frontend + Python FastAPI backend.
  * Push-to-Talk mic (`MediaRecorder` → Gemini Flash audio or `mlx-whisper`) + TTS playback.
  * 45-min phase timer, Case Packet loader, active Interviewer Agent, and `debrief.md` generator.
  * *Immediate usable value:* You can run your first Sokin mock case immediately.
* **Phase 2 — Embedded Excalidraw Multimodal Whiteboard (~1 session):**
  * Embed `@excalidraw/excalidraw` in the left pane.
  * Auto-capture PNG + JSON diff on every PTT release and pass to the multimodal Interviewer & Evaluator agents.
* **Phase 3 — Antigravity Skill / Case Generator Bridge (~1 session):**
  * Add a lightweight Antigravity skill/script that turns any `role-prep/*.md` + public docs (like `https://docs.sokin.com/`) into a realistic 3–4 page `case-packet.json` (including hidden facts & curveballs) with one command.

---

## 8. Open Decisions to Confirm Before Building
1. **STT / LLM Preference:** Prefer **Gemini API** (single key handles native audio STT + multimodal Excalidraw PNG + reasoning) or **local `mlx-whisper`** for STT + Gemini/Claude for reasoning? *(Recommendation: Gemini 2.5 Flash/Pro for both audio + whiteboard vision keeps the stack tiny and lets the model hear tone/hesitation!)*
2. **Interviewer Voice:** Do you want the interviewer to **speak back via TTS** (more realistic) or **text-only replies** (faster, quieter)? *(Recommendation: Toggleable TTS on by default, with text always visible.)*
3. **Case Library Seed:** Start with 2 Sokin-specific cases right away — **(1) API Foundation vs. MCP Prioritisation** (mirroring your previous tough interview!) and **(2) Redesigning `docs.sokin.com` + Sandbox for <1-Day First Payment**?
