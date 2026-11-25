import type {
  CaseSummary,
  GenerateCaseResponse,
  HealthResponse,
  SessionState,
  SessionSummary,
  TranscriptTurn,
  TurnResponse,
  WhiteboardSnapshotMeta,
} from './types';

async function handleJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) message = String(body.detail);
    } catch {
      // ignore parse failure
    }
    throw new Error(message);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health(): Promise<HealthResponse> {
    return fetch('/api/health').then((r) => handleJson<HealthResponse>(r));
  },

  listCases(): Promise<CaseSummary[]> {
    return fetch('/api/cases').then((r) => handleJson<CaseSummary[]>(r));
  },

  generateCase(params: {
    source_markdown: string;
    urls: string[];
    topic?: string;
    company?: string;
    role?: string;
    duration_minutes?: number;
  }): Promise<GenerateCaseResponse> {
    return fetch('/api/cases/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    }).then((r) => handleJson<GenerateCaseResponse>(r));
  },

  listSessions(): Promise<SessionSummary[]> {
    return fetch('/api/sessions').then((r) => handleJson<SessionSummary[]>(r));
  },

  getSession(sessionId: string): Promise<SessionState> {
    return fetch(`/api/sessions/${encodeURIComponent(sessionId)}`).then((r) =>
      handleJson<SessionState>(r),
    );
  },

  createSession(params: {
    case_id: string;
    silence_nudge_seconds: number;
    tts_enabled: boolean;
    tts_provider: 'browser' | 'elevenlabs';
    whiteboard_enabled: boolean;
  }): Promise<SessionState> {
    return fetch('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    }).then((r) => handleJson<SessionState>(r));
  },

  async synthesizeSpeech(text: string, signal?: AbortSignal): Promise<Blob> {
    const res = await fetch('/api/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
      signal,
    });
    if (!res.ok) {
      let message = `TTS request failed (${res.status})`;
      try {
        const body = await res.json();
        if (body?.detail) message = String(body.detail);
      } catch {
        // ignore parse failure
      }
      throw new Error(message);
    }
    return res.blob();
  },

  submitTurn(params: {
    sessionId: string;
    audioBlob: Blob | null;
    elapsedSeconds: number;
    speakingDurationSeconds: number;
    whiteboardPng?: Blob | null;
    whiteboardDiff?: Record<string, unknown> | null;
    whiteboardScene?: string | null;
  }): Promise<TurnResponse> {
    const form = new FormData();
    form.append('elapsed_seconds', String(Math.max(0, Math.floor(params.elapsedSeconds))));
    form.append('speaking_duration_seconds', params.speakingDurationSeconds.toFixed(1));
    if (params.audioBlob) {
      const ext = params.audioBlob.type.includes('mp4') ? 'm4a' : 'webm';
      form.append('audio', params.audioBlob, `turn.${ext}`);
    }
    if (params.whiteboardPng) {
      form.append('whiteboard_png', params.whiteboardPng, 'whiteboard.png');
    }
    if (params.whiteboardDiff) {
      form.append('whiteboard_diff', JSON.stringify(params.whiteboardDiff));
    }
    if (params.whiteboardScene) {
      form.append('whiteboard_scene', params.whiteboardScene);
    }
    return fetch(`/api/sessions/${encodeURIComponent(params.sessionId)}/turn`, {
      method: 'POST',
      body: form,
    }).then((r) => handleJson<TurnResponse>(r));
  },

  saveFinalWhiteboard(params: {
    sessionId: string;
    elapsedSeconds: number;
    elementCount: number;
    whiteboardPng: Blob | null;
    whiteboardScene: string | null;
  }): Promise<WhiteboardSnapshotMeta | null> {
    const form = new FormData();
    form.append('elapsed_seconds', String(Math.max(0, Math.floor(params.elapsedSeconds))));
    form.append('element_count', String(params.elementCount));
    if (params.whiteboardPng) {
      form.append('whiteboard_png', params.whiteboardPng, 'final.png');
    }
    if (params.whiteboardScene) {
      form.append('whiteboard_scene', params.whiteboardScene);
    }
    return fetch(`/api/sessions/${encodeURIComponent(params.sessionId)}/whiteboard`, {
      method: 'POST',
      body: form,
    }).then((r) => handleJson<WhiteboardSnapshotMeta | null>(r));
  },

  snapshotUrl(sessionId: string, filename: string): string {
    return `/api/sessions/${encodeURIComponent(sessionId)}/snapshots/${encodeURIComponent(filename)}`;
  },

  recordNudge(sessionId: string, elapsedSeconds: number): Promise<TranscriptTurn> {
    return fetch(`/api/sessions/${encodeURIComponent(sessionId)}/nudge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ elapsed_seconds: Math.max(0, Math.floor(elapsedSeconds)) }),
    }).then((r) => handleJson<TranscriptTurn>(r));
  },

  endSession(sessionId: string, elapsedSeconds: number): Promise<SessionState> {
    return fetch(`/api/sessions/${encodeURIComponent(sessionId)}/end`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ elapsed_seconds: Math.max(0, Math.floor(elapsedSeconds)) }),
    }).then((r) => handleJson<SessionState>(r));
  },
};
