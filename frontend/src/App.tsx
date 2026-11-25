import { useCallback, useEffect, useState } from 'react';
import { api } from './api';
import { DebriefView } from './components/DebriefView';
import { InterviewRoom } from './components/InterviewRoom';
import { Lobby } from './components/Lobby';
import type {
  CaseSummary,
  HealthResponse,
  SessionState,
  SessionSummary,
  TTSProvider,
} from './types';

type View = 'lobby' | 'interview' | 'debrief';

export function App() {
  const [view, setView] = useState<View>('lobby');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [activeSession, setActiveSession] = useState<SessionState | null>(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  const refreshLobbyData = useCallback(async () => {
    try {
      setLoadError(null);
      const [h, c, s] = await Promise.all([api.health(), api.listCases(), api.listSessions()]);
      setHealth(h);
      setCases(c);
      setSessions(s);
    } catch (err) {
      setLoadError(
        err instanceof Error
          ? `${err.message} — make sure the FastAPI backend is running on port 8000.`
          : 'Unable to reach backend on port 8000.',
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshLobbyData();
  }, [refreshLobbyData]);

  const handleStartSession = async (
    caseId: string,
    silenceNudgeSeconds: number,
    ttsEnabled: boolean,
    ttsProvider: TTSProvider,
  ) => {
    setStarting(true);
    try {
      const created = await api.createSession({
        case_id: caseId,
        silence_nudge_seconds: silenceNudgeSeconds,
        tts_enabled: ttsEnabled,
        tts_provider: ttsProvider,
      });
      setActiveSession(created);
      setView('interview');
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Failed to start session');
    } finally {
      setStarting(false);
    }
  };

  const handleOpenSession = async (sessionId: string) => {
    try {
      const loaded = await api.getSession(sessionId);
      setActiveSession(loaded);
      setView(loaded.status === 'completed' ? 'debrief' : 'interview');
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Failed to load session');
    }
  };

  const handleSessionCompleted = (completed: SessionState) => {
    setActiveSession(completed);
    setView('debrief');
    void refreshLobbyData();
  };

  const handleBackToLobby = () => {
    setActiveSession(null);
    setView('lobby');
    void refreshLobbyData();
  };

  if (loading) {
    return <div className="loading-screen">Loading Product Sense Interview Harness…</div>;
  }

  if (loadError && view === 'lobby' && cases.length === 0) {
    return (
      <div className="loading-screen">
        <div className="error-card">
          <h2>Backend Unavailable</h2>
          <p>{loadError}</p>
          <button type="button" className="primary-btn" onClick={() => void refreshLobbyData()}>
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  if (view === 'interview' && activeSession) {
    return (
      <InterviewRoom
        initialSession={activeSession}
        elevenlabsAvailable={Boolean(health?.elevenlabs_available)}
        onSessionCompleted={handleSessionCompleted}
        onExitToLobby={handleBackToLobby}
      />
    );
  }

  if (view === 'debrief' && activeSession) {
    return <DebriefView session={activeSession} onBackToLobby={handleBackToLobby} />;
  }

  return (
    <Lobby
      health={health}
      cases={cases}
      sessions={sessions}
      starting={starting}
      onStartSession={(caseId, nudge, tts, provider) =>
        void handleStartSession(caseId, nudge, tts, provider)
      }
      onOpenSession={(id) => void handleOpenSession(id)}
    />
  );
}
