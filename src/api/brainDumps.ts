import { apiClient } from "./client";
import type { BrainDump, Session, Suggestion } from "../types/api";

export interface BrainDumpResponse {
  session: Session;
  brain_dump: BrainDump;
  suggestions: Suggestion[];
}

export async function createBrainDump(rawText: string, sessionId?: number) {
  const response = await apiClient.post<BrainDumpResponse>("/brain-dumps", {
    raw_text: rawText,
    session_id: sessionId,
  });
  return response.data;
}
