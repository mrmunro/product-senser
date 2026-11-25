import { useState } from 'react';
import {
  Clock,
  FileText,
  Mic,
  Play,
  Sparkles,
  Users,
  Volume2,
  VolumeX,
} from 'lucide-react';
import type { CaseSummary, HealthResponse, SessionSummary } from '../types';

interface LobbyProps {
  health: HealthResponse | null;
  cases: CaseSummary[];
  sessions: SessionSummary[];
  starting: boolean;
  onStartSession: (caseId: string, silenceNudgeSeconds: number, ttsEnabled: boolean) => void;
  onOpenSession: (sessionId: string) => void;
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s.toString().padStart(2, '0')}s`;
}

export function Lobby({
  health,
  cases,
  sessions,
  starting,
  onStartSession,
  onOpenSession,
}: LobbyProps) {
  const [selectedCaseId, setSelectedCaseId] = useState<string>(cases[0]?.id ?? '');
  const [silenceNudgeSeconds, setSilenceNudgeSeconds] = useState<number>(60);
  const [ttsEnabled, setTtsEnabled] = useState<boolean>(true);

  const activeCaseId = selectedCaseId || cases[0]?.id || '';
  const selectedCase = cases.find((c) => c.id === activeCaseId) ?? cases[0];

  return (
    <div className="lobby-shell">
      <header className="lobby-header">
        <div>
          <div className="brand-row">
            <span className="brand-badge">Phase 1 · Voice-First Simulator</span>
            {health && (
              <span className={`mode-pill ${health.demo_mode ? 'demo' : 'live'}`}>
                <Sparkles size={13} />
                {health.demo_mode
                  ? 'Demo Mode (set GEMINI_API_KEY in .env for live audio)'
                  : `Live Gemini (${health.interviewer_model})`}
              </span>
            )}
          </div>
          <h1>Product Sense Interview Harness</h1>
          <p className="subtitle">
            45-minute, voice-only Push-to-Talk simulator with deterministic phase pacing, hidden case facts,
            stakeholder curveballs, and scored post-session debriefs.
          </p>
        </div>
      </header>

      <main className="lobby-grid">
        <section className="lobby-main">
          <div className="section-title-row">
            <h2>1. Select Case Packet</h2>
            <span className="muted">{cases.length} seeded Sokin cases</span>
          </div>

          <div className="case-grid">
            {cases.map((c) => {
              const isSelected = c.id === activeCaseId;
              return (
                <button
                  key={c.id}
                  type="button"
                  className={`case-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => setSelectedCaseId(c.id)}
                >
                  <div className="case-card-top">
                    <span className="company-pill">{c.company}</span>
                    <span className="meta-pill">
                      <Clock size={12} /> {c.duration_minutes} min
                    </span>
                  </div>
                  <h3>{c.title}</h3>
                  <p className="case-role">{c.role}</p>
                  <div className="tag-row">
                    {c.tags.map((tag) => (
                      <span key={tag} className="tag">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="interviewer-mini">
                    <Users size={13} />
                    <span>{c.interviewers.map((p) => `${p.name} (${p.role})`).join(' · ')}</span>
                  </div>
                </button>
              );
            })}
          </div>

          {selectedCase && (
            <div className="panel-box launch-panel">
              <div className="launch-details">
                <h3>Evaluation Focus for This Case</h3>
                <ul className="focus-list">
                  {selectedCase.evaluation_focus.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="launch-controls">
                <div className="control-group">
                  <label htmlFor="silence-select">Thinking-Out-Loud Silence Nudge</label>
                  <select
                    id="silence-select"
                    value={silenceNudgeSeconds}
                    onChange={(e) => setSilenceNudgeSeconds(Number(e.target.value))}
                  >
                    <option value={45}>45 seconds</option>
                    <option value={60}>60 seconds (Recommended)</option>
                    <option value={90}>90 seconds</option>
                    <option value={0}>Off</option>
                  </select>
                </div>

                <div className="control-group">
                  <label>Interviewer Voice (TTS)</label>
                  <button
                    type="button"
                    className={`toggle-btn ${ttsEnabled ? 'on' : 'off'}`}
                    onClick={() => setTtsEnabled((v) => !v)}
                  >
                    {ttsEnabled ? <Volume2 size={15} /> : <VolumeX size={15} />}
                    {ttsEnabled ? 'Voice On (with text transcript)' : 'Text Only'}
                  </button>
                </div>

                <button
                  type="button"
                  className="primary-btn start-btn"
                  disabled={starting || !activeCaseId}
                  onClick={() => onStartSession(activeCaseId, silenceNudgeSeconds, ttsEnabled)}
                >
                  <Mic size={18} />
                  {starting ? 'Starting Session…' : `Start ${selectedCase.duration_minutes}-Min Voice Interview`}
                </button>
                <p className="voice-rule-note">
                  Voice-only mode is enforced during the interview — hold <code>Spacebar</code> or click to speak.
                </p>
              </div>
            </div>
          )}
        </section>

        <aside className="lobby-sidebar">
          <div className="section-title-row">
            <h2>Saved Sessions & Debriefs</h2>
            <span className="muted">{sessions.length}</span>
          </div>

          {sessions.length === 0 ? (
            <div className="empty-sessions">
              <FileText size={24} />
              <p>No saved sessions yet. Completed runs save their transcript and scored <code>debrief.md</code> under <code>sessions/</code>.</p>
            </div>
          ) : (
            <div className="session-list">
              {sessions.map((s) => (
                <button
                  key={s.session_id}
                  type="button"
                  className="session-item"
                  onClick={() => onOpenSession(s.session_id)}
                >
                  <div className="session-item-top">
                    <span className={`status-dot ${s.status}`}>{s.status === 'completed' ? 'Debrief Ready' : 'In Progress'}</span>
                    <span className="muted">{formatDuration(s.elapsed_seconds)}</span>
                  </div>
                  <div className="session-item-title">{s.title}</div>
                  <div className="session-item-meta">
                    <span>{new Date(s.started_at).toLocaleDateString()}</span>
                    <span>· {s.turn_count} turns</span>
                    {s.demo_mode && <span>· Demo</span>}
                  </div>
                  <span className="open-link">
                    <Play size={12} /> {s.status === 'completed' ? 'View Debrief' : 'Resume'}
                  </span>
                </button>
              ))}
            </div>
          )}
        </aside>
      </main>
    </div>
  );
}
