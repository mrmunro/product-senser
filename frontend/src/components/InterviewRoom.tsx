import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  AlertTriangle,
  BookOpen,
  Clock,
  Image as ImageIcon,
  Layers,
  Loader2,
  Mic,
  Square,
  StopCircle,
  Volume2,
  VolumeX,
} from 'lucide-react';
import { api } from '../api';
import { usePushToTalk } from '../hooks/usePushToTalk';
import { useTTS } from '../hooks/useTTS';
import type { PhaseInfo, SessionState, TranscriptTurn } from '../types';
import { WhiteboardPane, type WhiteboardPaneHandle } from './WhiteboardPane';

interface InterviewRoomProps {
  initialSession: SessionState;
  elevenlabsAvailable: boolean;
  onSessionCompleted: (completed: SessionState) => void;
  onExitToLobby: () => void;
}

function formatClock(totalSeconds: number): string {
  const clamped = Math.max(0, Math.floor(totalSeconds));
  const m = Math.floor(clamped / 60);
  const s = clamped % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function getPhaseForElapsed(phases: PhaseInfo[], elapsedSeconds: number): PhaseInfo {
  const elapsedMin = elapsedSeconds / 60;
  for (const p of phases) {
    if (elapsedMin < p.end_minute) return p;
  }
  return phases[phases.length - 1];
}

export function InterviewRoom({
  initialSession,
  elevenlabsAvailable,
  onSessionCompleted,
  onExitToLobby,
}: InterviewRoomProps) {
  const [session, setSession] = useState<SessionState>(initialSession);
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(initialSession.elapsed_seconds);
  const [silenceSeconds, setSilenceSeconds] = useState<number>(0);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [ending, setEnding] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [audioOnlyMode, setAudioOnlyMode] = useState<boolean>(!initialSession.whiteboard_enabled);
  const [leftTab, setLeftTab] = useState<'brief' | 'whiteboard'>('brief');

  const logEndRef = useRef<HTMLDivElement | null>(null);
  const whiteboardRef = useRef<WhiteboardPaneHandle | null>(null);
  const nudgeInFlightRef = useRef(false);
  const hasEndedRef = useRef(false);
  const spokeOpeningRef = useRef(false);

  const tts = useTTS(
    initialSession.tts_enabled,
    initialSession.tts_provider ?? 'browser',
    elevenlabsAvailable,
  );

  const totalDurationSeconds = session.duration_minutes * 60;
  const remainingSeconds = Math.max(0, totalDurationSeconds - elapsedSeconds);
  const readingGraceSeconds = session.reading_grace_seconds ?? 120;
  const hasSpokenOnce = useMemo(
    () => session.turns.some((t) => t.role === 'candidate'),
    [session.turns],
  );
  const isInReadingGrace = !hasSpokenOnce && elapsedSeconds < readingGraceSeconds;
  const readingRemainingSeconds = Math.max(0, readingGraceSeconds - elapsedSeconds);
  const currentPhase = useMemo(
    () => getPhaseForElapsed(session.phases, elapsedSeconds),
    [session.phases, elapsedSeconds],
  );

  // Speak opening turn once on mount
  useEffect(() => {
    if (!spokeOpeningRef.current && session.turns.length > 0) {
      spokeOpeningRef.current = true;
      const last = session.turns[session.turns.length - 1];
      if (last.role === 'interviewer') {
        tts.speak(last.text);
      }
    }
  }, [session.turns, tts]);

  // Auto-scroll conversation log
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [session.turns.length, submitting]);

  const handleEndSession = useCallback(async () => {
    if (hasEndedRef.current) return;
    hasEndedRef.current = true;
    tts.stop();
    setEnding(true);
    setError(null);
    try {
      if (!audioOnlyMode && whiteboardRef.current) {
        const finalCapture = await whiteboardRef.current.captureSnapshot().catch(() => null);
        if (finalCapture) {
          await api
            .saveFinalWhiteboard({
              sessionId: session.session_id,
              elapsedSeconds,
              elementCount: finalCapture.elementCount,
              whiteboardPng: finalCapture.pngBlob,
              whiteboardScene: finalCapture.sceneJson,
            })
            .catch(() => null);
        }
      }
      const completed = await api.endSession(session.session_id, elapsedSeconds);
      onSessionCompleted(completed);
    } catch (err) {
      hasEndedRef.current = false;
      setEnding(false);
      setError(err instanceof Error ? err.message : 'Failed to generate debrief');
    }
  }, [audioOnlyMode, elapsedSeconds, onSessionCompleted, session.session_id, tts]);

  const handleRecordingComplete = useCallback(
    async (blob: Blob, durationSeconds: number) => {
      setSubmitting(true);
      setError(null);
      setSilenceSeconds(0);
      try {
        const wbCapture =
          !audioOnlyMode && whiteboardRef.current
            ? await whiteboardRef.current.captureSnapshot().catch(() => null)
            : null;

        const res = await api.submitTurn({
          sessionId: session.session_id,
          audioBlob: blob,
          elapsedSeconds,
          speakingDurationSeconds: durationSeconds,
          whiteboardPng: wbCapture?.pngBlob ?? null,
          whiteboardDiff: wbCapture
            ? (wbCapture.diff as unknown as Record<string, unknown>)
            : null,
          whiteboardScene: wbCapture?.sceneJson ?? null,
        });

        setSession((prev) => ({
          ...prev,
          current_phase: res.current_phase,
          elapsed_seconds: res.elapsed_seconds,
          curveballs_injected: res.curveballs_injected,
          whiteboard_snapshots: res.whiteboard_snapshot
            ? [...prev.whiteboard_snapshots, res.whiteboard_snapshot]
            : prev.whiteboard_snapshots,
          turns: [...prev.turns, res.candidate_turn, res.interviewer_turn],
        }));

        tts.speak(res.interviewer_turn.text);

        if (res.should_hard_stop) {
          window.setTimeout(() => {
            void handleEndSession();
          }, 2500);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to process your spoken turn');
      } finally {
        setSubmitting(false);
        setSilenceSeconds(0);
      }
    },
    [audioOnlyMode, elapsedSeconds, handleEndSession, session.session_id, tts],
  );

  const ptt = usePushToTalk({
    disabled: submitting || ending || remainingSeconds <= 0,
    onRecordingStart: () => {
      tts.stop();
      setSilenceSeconds(0);
    },
    onRecordingComplete: handleRecordingComplete,
  });

  // Main 1-second session clock & silence nudge tracker
  useEffect(() => {
    if (ending || session.status !== 'active') return;

    const id = window.setInterval(() => {
      setElapsedSeconds((prev) => {
        const next = prev + 1;
        if (next >= totalDurationSeconds && !hasEndedRef.current) {
          void handleEndSession();
        }
        return next;
      });

      if (!isInReadingGrace && !ptt.isRecording && !submitting && session.silence_nudge_seconds > 0) {
        setSilenceSeconds((prev) => prev + 1);
      }
    }, 1000);

    return () => window.clearInterval(id);
  }, [ending, handleEndSession, isInReadingGrace, ptt.isRecording, session.silence_nudge_seconds, session.status, submitting, totalDurationSeconds]);

  // Trigger Thinking-Out-Loud silence nudge when threshold reached
  useEffect(() => {
    if (
      isInReadingGrace ||
      session.silence_nudge_seconds <= 0 ||
      ptt.isRecording ||
      submitting ||
      ending ||
      nudgeInFlightRef.current
    ) {
      return;
    }

    if (silenceSeconds >= session.silence_nudge_seconds) {
      nudgeInFlightRef.current = true;
      setSilenceSeconds(0);
      api
        .recordNudge(session.session_id, elapsedSeconds)
        .then((nudgeTurn: TranscriptTurn) => {
          setSession((prev) => ({
            ...prev,
            turns: [...prev.turns, nudgeTurn],
          }));
          tts.speak(nudgeTurn.text);
        })
        .catch(() => {
          // Non-fatal
        })
        .finally(() => {
          nudgeInFlightRef.current = false;
        });
    }
  }, [
    elapsedSeconds,
    ending,
    isInReadingGrace,
    ptt.isRecording,
    session.session_id,
    session.silence_nudge_seconds,
    silenceSeconds,
    submitting,
    tts,
  ]);

  const timerUrgency =
    remainingSeconds <= 120 ? 'critical' : remainingSeconds <= 420 ? 'warning' : 'normal';

  return (
    <div className="room-shell">
      <header className="room-topbar">
        <div className="room-title-block">
          <button type="button" className="ghost-btn" onClick={onExitToLobby} disabled={ending}>
            ← Lobby
          </button>
          <div>
            <div className="room-case-title">{session.title}</div>
            <div className="room-case-sub">
              {session.company} · {session.role}
              {session.demo_mode && <span className="inline-demo-badge">Demo Mode</span>}
            </div>
          </div>
        </div>

        <div className="room-topbar-right">
          <div className={`countdown-chip ${timerUrgency}`} title="Remaining interview time">
            <Clock size={16} />
            <span>{formatClock(remainingSeconds)}</span>
            <small>/ {session.duration_minutes}:00</small>
          </div>

          <button
            type="button"
            className="ghost-btn"
            onClick={() => tts.setEnabled(!tts.enabled)}
            title={tts.enabled ? 'Mute interviewer voice' : 'Unmute interviewer voice'}
          >
            {tts.enabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
            <span>{tts.enabled ? 'Voice On' : 'Muted'}</span>
          </button>

          {tts.enabled && elevenlabsAvailable && (
            <button
              type="button"
              className="ghost-btn"
              onClick={() =>
                tts.setProvider(tts.provider === 'elevenlabs' ? 'browser' : 'elevenlabs')
              }
              title="Toggle between Browser default voice and ElevenLabs voice"
            >
              <span>{tts.provider === 'elevenlabs' ? 'Voice: ElevenLabs' : 'Voice: Browser'}</span>
            </button>
          )}

          <button
            type="button"
            className="danger-btn"
            disabled={ending}
            onClick={() => void handleEndSession()}
          >
            {ending ? <Loader2 size={15} className="spin" /> : <StopCircle size={15} />}
            <span>{ending ? 'Generating Debrief…' : 'End & Debrief'}</span>
          </button>
        </div>
      </header>

      <div className="phase-strip">
        {session.phases.map((p) => {
          const isCurrent = p.id === currentPhase.id;
          const isDone = elapsedSeconds / 60 >= p.end_minute;
          return (
            <div
              key={p.id}
              className={`phase-pill ${isCurrent ? 'active' : isDone ? 'done' : ''}`}
              title={`${p.name} (${p.start_minute}–${p.end_minute}m): ${p.objective}`}
            >
              <span className="phase-num">{p.number}</span>
              <span className="phase-name">{p.name}</span>
              <span className="phase-window">
                {Math.round(p.start_minute)}–{Math.round(p.end_minute)}m
              </span>
            </div>
          );
        })}
      </div>

      <div className="room-panes">
        {/* LEFT PANE: Case Brief + Embedded Excalidraw Whiteboard */}
        <section className="left-pane">
          <div className="pane-tabs pane-tabs-between">
            <div className="pane-tabs-group">
              <button
                type="button"
                className={`tab-btn ${leftTab === 'brief' ? 'active' : ''}`}
                onClick={() => setLeftTab('brief')}
              >
                <BookOpen size={15} /> Case Brief
              </button>
              {!audioOnlyMode && (
                <button
                  type="button"
                  className={`tab-btn ${leftTab === 'whiteboard' ? 'active' : ''}`}
                  onClick={() => setLeftTab('whiteboard')}
                >
                  <Layers size={15} /> Whiteboard
                  {session.whiteboard_snapshots.length > 0 && (
                    <span className="phase2-pill">{session.whiteboard_snapshots.length}</span>
                  )}
                </button>
              )}
            </div>

            <button
              type="button"
              className={`wb-mode-toggle ${audioOnlyMode ? 'audio-only' : ''}`}
              onClick={() => {
                setAudioOnlyMode((prev) => {
                  const next = !prev;
                  if (next) setLeftTab('brief');
                  return next;
                });
              }}
              title="Toggle between Voice + Whiteboard and Audio-Only Mode"
            >
              {audioOnlyMode ? 'Audio-Only Mode (Enable Whiteboard)' : 'Switch to Audio-Only'}
            </button>
          </div>

          <div
            className="brief-scroll markdown-body"
            style={{ display: leftTab === 'brief' || audioOnlyMode ? 'block' : 'none' }}
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {session.candidate_brief_markdown}
            </ReactMarkdown>
          </div>

          {!audioOnlyMode && (
            <div
              className="whiteboard-tab-host"
              style={{ display: leftTab === 'whiteboard' ? 'flex' : 'none' }}
            >
              <WhiteboardPane ref={whiteboardRef} />
            </div>
          )}
        </section>

        {/* RIGHT PANE: Interview Console */}
        <section className="right-pane">
          <div className="phase-objective-bar">
            <div>
              <strong>
                Phase {currentPhase.number}: {currentPhase.name}
              </strong>
              <p>{currentPhase.objective}</p>
            </div>
            {session.silence_nudge_seconds > 0 && (
              isInReadingGrace ? (
                <div
                  className="silence-meter reading-grace"
                  title="2-minute reading grace period before the silence nudge starts — start speaking whenever you're ready"
                >
                  <span>Reading Time</span>
                  <strong>{formatClock(readingRemainingSeconds)} left</strong>
                </div>
              ) : (
                <div className="silence-meter" title="Silence nudge countdown">
                  <span>Silence</span>
                  <strong>
                    {silenceSeconds}s / {session.silence_nudge_seconds}s
                  </strong>
                </div>
              )
            )}
          </div>

          <div className="transcript-scroll">
            {session.turns.map((turn) => (
              <div
                key={turn.id}
                className={`turn-bubble ${turn.role} ${turn.is_nudge ? 'nudge' : ''} ${
                  turn.curveball_index !== null ? 'curveball' : ''
                }`}
              >
                <div className="turn-header">
                  <div className="turn-speaker">
                    <strong>{turn.speaker_name}</strong>
                    {turn.speaker_role && <span className="muted"> · {turn.speaker_role}</span>}
                    {turn.is_nudge && <span className="mini-tag nudge-tag">Thinking-Out-Loud Nudge</span>}
                    {turn.curveball_index !== null && (
                      <span className="mini-tag curveball-tag">Curveball</span>
                    )}
                  </div>
                  <div className="turn-meta">
                    <span>{formatClock(turn.elapsed_seconds)}</span>
                    {turn.speaking_duration_seconds > 0 && (
                      <span>· {Math.round(turn.speaking_duration_seconds)}s</span>
                    )}
                    {turn.role === 'interviewer' && tts.supported && (
                      <button
                        type="button"
                        className="icon-btn"
                        onClick={() => tts.speak(turn.text, true)}
                        title="Replay interviewer audio"
                      >
                        <Volume2 size={13} />
                      </button>
                    )}
                  </div>
                </div>
                <p className="turn-text">{turn.text}</p>
                {turn.whiteboard_snapshot && (
                  <div className="turn-wb-badge">
                    <ImageIcon size={13} />
                    <span>
                      Whiteboard captured: {turn.whiteboard_diff_summary || turn.whiteboard_snapshot}
                    </span>
                  </div>
                )}
              </div>
            ))}

            {submitting && (
              <div className="turn-bubble system">
                <Loader2 size={15} className="spin" />
                <span>Transcribing your answer and waiting for the panel…</span>
              </div>
            )}
            <div ref={logEndRef} />
          </div>

          <div className="ptt-dock">
            {(error || ptt.micError || tts.ttsWarning) && (
              <div className="error-banner">
                <AlertTriangle size={15} />
                <span>{error || ptt.micError || tts.ttsWarning}</span>
              </div>
            )}

            <div className="ptt-row">
              <button
                type="button"
                className={`ptt-btn ${ptt.isRecording ? `recording ${ptt.turnLengthStatus}` : ''}`}
                disabled={submitting || ending || remainingSeconds <= 0}
                onClick={ptt.toggleRecording}
              >
                {ptt.isRecording ? (
                  <>
                    <Square size={18} />
                    <span>Done Speaking</span>
                    <span className={`turn-timer ${ptt.turnLengthStatus}`}>
                      {formatClock(ptt.recordingSeconds)}
                    </span>
                  </>
                ) : (
                  <>
                    <Mic size={18} />
                    <span>{submitting ? 'Processing…' : 'Start Speaking (or Hold Spacebar)'}</span>
                  </>
                )}
              </button>
            </div>

            <div className="ptt-hints">
              <span>Voice-only enforced (no typing)</span>
              <span>
                Turn length: <strong className="amber-text">2:30 amber</strong> ·{' '}
                <strong className="red-text">3:30 red</strong>
              </span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
