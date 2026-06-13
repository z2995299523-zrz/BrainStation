import type { SessionData, FeynmanResult, ProgressSummary } from '../types';

const BASE_URL = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  getSessionToday: (subject?: string) =>
    request<SessionData>(`/session/today${subject ? `?subject=${subject}` : ''}`),
  submitAnswer: (data: {
    session_id: number;
    question_id: string;
    step_type: string;
    user_answer: unknown;
    confidence?: number;
    time_spent_sec?: number;
  }) =>
    request<{
      is_correct: boolean | null;
      explanation: string;
      mastery_update: Record<string, unknown>;
    }>('/session/answer', { method: 'POST', body: JSON.stringify(data) }),

  submitFeynman: (data: {
    session_id: number;
    explanation: string;
    deep_choice?: string;
    deep_answer?: string;
  }) =>
    request<FeynmanResult>('/session/feynman', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  submitCalibrate: (data: { session_id: number; confidence: number; thought_diary: string }) =>
    request<{ status: string }>('/session/calibrate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  completeSession: (data: { session_id: number; total_time_sec?: number }) =>
    request<{ status: string }>('/session/complete', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getProgressSummary: (subject?: string) =>
    request<ProgressSummary>(`/progress/summary${subject ? `?subject=${subject}` : ''}`),
  getProgressTree: (subject?: string) =>
    request<unknown>(`/progress/tree${subject ? `?subject=${subject}` : ''}`),
  getDiary: () => request<Array<{ id: number; session_date: string; reflection: string }>>('/progress/diary'),

  // Admin
  getSm2State: () => request<{ nodes: Array<Record<string, unknown>> }>('/admin/sm2-state'),
  overrideSm2: (data: Record<string, unknown>) =>
    request<{ status: string }>('/admin/sm2-override', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  reloadContent: () =>
    request<{ status: string; nodes_loaded: number; questions_loaded: number }>(
      '/admin/reload-content',
      { method: 'POST' }
    ),
  updateConfig: (data: { param_path: string; new_value: string }) =>
    request<{ status: string }>('/admin/config-update', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};
