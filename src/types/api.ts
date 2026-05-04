export type Reaction = "do" | "snooze" | "pass" | "make_smaller" | "capture_only";
export type ActionStatus = "active" | "completed" | "aborted";
export type EffortLevel = "quiet" | "gentle" | "neutral" | "tiny" | "nano";

export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface Session {
  id: number;
  context_note: string | null;
  created_at: string;
}

export interface BrainDump {
  id: number;
  session_id: number;
  raw_text: string;
  created_at: string;
}

export interface Suggestion {
  id: number;
  session_id: number;
  brain_dump_id: number | null;
  parent_suggestion_id: number | null;
  generation_type: "original" | "smaller" | "safety_net";
  source?: "rule_based" | "ai";
  title: string;
  micro_step: string;
  effort_level: EffortLevel;
  created_at: string;
}

export interface Action {
  id: number;
  session_id: number;
  suggestion_id: number | null;
  title: string;
  micro_step: string;
  status: ActionStatus;
  completion_note: string | null;
  abort_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface Feedback {
  id: number;
  session_id: number;
  suggestion_id: number | null;
  action_id: number | null;
  reaction: Reaction;
  note: string | null;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
}

export interface HistoryResponse {
  sessions: Session[];
  brain_dumps: BrainDump[];
  actions: Action[];
  feedback: Feedback[];
}
