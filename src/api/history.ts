import { apiClient } from "./client";
import type { HistoryResponse } from "../types/api";

export async function getHistory(limit = 20) {
  const response = await apiClient.get<HistoryResponse>("/me/history", { params: { limit } });
  return response.data;
}
