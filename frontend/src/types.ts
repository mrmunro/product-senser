export type TTSProvider = 'browser' | 'elevenlabs';

export type PhaseId =
  | 'brief_clarify'
  | 'framing_strategy'
  | 'deep_dive'
  | 'curveball'
  | 'executive_wrapup'
  | 'hard_stop';

export interface PhaseInfo {
  id: PhaseId;
  number: number;
  name: string;
  start_minute: number;
  end_minute: number;
  objective: string;
  interviewer_behavior: string;
}

export interface InterviewerPersona {
  name: string;
  role: string;
  focus: string;
}

export interface CaseSummary {
  id: string;
  title: string;
  company: string;
  role: string;
  duration_minutes: number;
  difficulty: string;
  tags: string[];
  interviewers: InterviewerPersona[];
  evaluation_focus: string[];
}

export interface WhiteboardSnapshotMeta {
  filename: string;
  turn_id: string | null;
  phase: PhaseId;
  elapsed_seconds: number;
  element_count: number;
  diff_summary: string | null;
  timestamp: string;
}

export interface TranscriptTurn {
  id: string;
  role: 'candidate' | 'interviewer' | 'system';
  speaker_name: string;
  speaker_role: string;
  text: string;
  phase: PhaseId;
  elapsed_seconds: number;
  speaking_duration_seconds: number;
  timestamp: string;
  is_nudge: boolean;
  curveball_index: number | null;
  delivery_notes: string | null;
  whiteboard_snapshot: string | null;
  whiteboard_diff_summary: string | null;
}

export interface SessionState {
  session_id: string;
  case_id: string;
  title: string;
  company: string;
  role: string;
  started_at: string;
  ended_at: string | null;
  status: 'active' | 'completed';
  duration_minutes: number;
  reading_grace_seconds: number;
  silence_nudge_seconds: number;
  tts_enabled: boolean;
  tts_provider: TTSProvider;
  whiteboard_enabled: boolean;
  demo_mode: boolean;
  current_phase: PhaseInfo;
  phases: PhaseInfo[];
  elapsed_seconds: number;
  curveballs_injected: number[];
  interviewers: InterviewerPersona[];
  candidate_brief_markdown: string;
  turns: TranscriptTurn[];
  whiteboard_snapshots: WhiteboardSnapshotMeta[];
  has_final_excalidraw: boolean;
  debrief_markdown: string | null;
}

export interface SessionSummary {
  session_id: string;
  case_id: string;
  title: string;
  company: string;
  role: string;
  started_at: string;
  ended_at: string | null;
  status: 'active' | 'completed';
  elapsed_seconds: number;
  turn_count: number;
  has_debrief: boolean;
  demo_mode: boolean;
}

export interface TurnResponse {
  candidate_turn: TranscriptTurn;
  interviewer_turn: TranscriptTurn;
  current_phase: PhaseInfo;
  elapsed_seconds: number;
  curveballs_injected: number[];
  whiteboard_snapshot: WhiteboardSnapshotMeta | null;
  should_hard_stop: boolean;
}

export interface HealthResponse {
  status: string;
  demo_mode: boolean;
  interviewer_model: string;
  evaluator_model: string;
  elevenlabs_available: boolean;
  elevenlabs_voice_id: string | null;
}

export interface GenerateCaseResponse {
  case: CaseSummary;
  warnings: string[];
  used_demo_mode: boolean;
}
