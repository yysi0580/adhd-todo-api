import { apiClient } from "./client";
import type { Feedback, Reaction, Suggestion } from "../types/api";

export interface FeedbackResponse {
  feedback: Feedback;
  action_id: number | null;
  smaller_suggestions: Suggestion[];
}

export async function createFeedback(
  sessionId: number,
  suggestionId: number,
  reaction: Reaction,
  note?: string,
) {
  const response = await apiClient.post<FeedbackResponse>("/feedback", {
    session_id: sessionId,
    suggestion_id: suggestionId,
    reaction,
    note,
  });
  return response.data;
}
