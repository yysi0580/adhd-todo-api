import { apiClient } from "./client";
import type { AuthTokens, User } from "../types/api";

export async function register(email: string, password: string) {
  const response = await apiClient.post<User>("/auth/register", { email, password });
  return response.data;
}

export async function login(email: string, password: string) {
  const response = await apiClient.post<AuthTokens>("/auth/login", { email, password });
  return response.data;
}

export async function refresh(refreshToken: string) {
  const response = await apiClient.post<AuthTokens>("/auth/refresh", {
    refresh_token: refreshToken,
  });
  return response.data;
}

export async function me() {
  const response = await apiClient.get<User>("/users/me");
  return response.data;
}
