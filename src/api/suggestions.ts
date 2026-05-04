import { apiClient } from "./client";
import type { Suggestion } from "../types/api";

export async function listSuggestions(sessionId: number) {
  const response = await apiClient.get<Suggestion[]>(`/sessions/${sessionId}/suggestions`);
  return response.data;
}

export async function makeSmaller(suggestionId: number) {
  const response = await apiClient.post<Suggestion[]>(
    `/suggestions/${suggestionId}/make-smaller`,
  );
  return response.data;
}
