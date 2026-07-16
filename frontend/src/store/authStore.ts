import { create } from "zustand";

interface AuthState {
  isAuthenticated: boolean;
  setAuthenticated: (auth: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  setAuthenticated: (auth) => set({ isAuthenticated: auth }),
  logout: () => set({ isAuthenticated: false }),
}));
