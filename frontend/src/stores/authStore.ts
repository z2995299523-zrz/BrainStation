import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type UserRole = 'learner' | 'examiner' | 'admin';

interface AuthUser {
  id: number;
  username: string;
  role: UserRole;
}

interface AuthState {
  token: string | null;
  user: AuthUser | null;
  loading: boolean;
  error: string | null;

  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const API_BASE = '/api/auth';

async function authRequest<T>(path: string, body: Record<string, string>): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({ detail: '请求失败' }));
    throw new Error(data.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      loading: false,
      error: null,

      login: async (username, password) => {
        set({ loading: true, error: null });
        try {
          const data = await authRequest<{ access_token: string; user: AuthUser }>(
            '/login',
            { username, password },
          );
          set({ token: data.access_token, user: data.user, loading: false });
        } catch (e) {
          set({ error: (e as Error).message, loading: false });
          throw e;
        }
      },

      register: async (username, password) => {
        set({ loading: true, error: null });
        try {
          const data = await authRequest<{ access_token: string; user: AuthUser }>(
            '/register',
            { username, password },
          );
          set({ token: data.access_token, user: data.user, loading: false });
        } catch (e) {
          set({ error: (e as Error).message, loading: false });
          throw e;
        }
      },

      logout: () => {
        set({ token: null, user: null, error: null });
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
      }),
    },
  ),
);
