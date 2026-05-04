import { create } from "zustand";

import type { User } from "../types/api";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUser: (user: User | null) => void;
  logout: () => void;
}

const accessKey = "decide.accessToken";
const refreshKey = "decide.refreshToken";

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem(accessKey),
  refreshToken: localStorage.getItem(refreshKey),
  user: null,
  setTokens: (accessToken, refreshToken) => {
    localStorage.setItem(accessKey, accessToken);
    localStorage.setItem(refreshKey, refreshToken);
    set({ accessToken, refreshToken });
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem(accessKey);
    localStorage.removeItem(refreshKey);
    set({ accessToken: null, refreshToken: null, user: null });
  },
}));
