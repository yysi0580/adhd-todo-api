import { apiClient } from "./client";
import type { Action } from "../types/api";

export async function createAction(sessionId: number, suggestionId?: number) {
  const response = await apiClient.post<Action>("/actions", {
    session_id: sessionId,
    suggestion_id: suggestionId,
  });
  return response.data;
}

export async function completeAction(actionId: number, note?: string) {
  const response = await apiClient.post<Action>(`/actions/${actionId}/complete`, { note });
  return response.data;
}

export async function abortAction(actionId: number, reason?: string) {
  const response = await apiClient.post<Action>(`/actions/${actionId}/abort`, { reason });
  return response.data;
}
