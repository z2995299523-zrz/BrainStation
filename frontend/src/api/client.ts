import type {
  ProgressSummary,
  ChapterContent,
  AnswerFeedback,
  PracticeQuestion,
  ChatSessionData,
  AIMessage,
  ExamListItem,
  ExamDetail,
  ExamAttemptData,
  ExamAnswerResult,
  ExamResultData,
  ExamManageItem,
  ExamResultSummary,
} from '../types';
import { useAuthStore } from '../stores/authStore';

const BASE_URL = '/api';

function getAuthHeaders(): Record<string, string> {
  const token = useAuthStore.getState().token;
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`API error: ${res.status} ${res.statusText}${body ? ` — ${body}` : ''}`);
  }
  return res.json();
}

export const api = {
  // ── 章节内容 ──
  getChapter: (slug: string, stage: string = 'concept') =>
    request<ChapterContent>(`/content/chapter?slug=${encodeURIComponent(slug)}&stage=${stage}`),

  submitAnswer: (data: {
    chapter_slug: string;
    question_id: string;
    user_answer: string;
    difficulty?: number;
    layer?: string;
  }) =>
    request<AnswerFeedback>('/content/submit-answer', {
      method: 'POST',
      body: JSON.stringify({
        chapter_slug: data.chapter_slug,
        question_id: data.question_id,
        user_answer: data.user_answer,
        difficulty: data.difficulty ?? 1,
        layer: data.layer ?? 'operation',
      }),
    }),

  // ── AI ──
  askAI: (
    data: { chapter_slug: string; current_stage: string; current_position: string; question: string; history?: Array<{role: string; content: string}> },
    onChunk: (text: string) => void,
    onDone: () => void,
    onError: (err: Error) => void,
  ): AbortController => {
    const controller = new AbortController();
    fetch(`${BASE_URL}/ai/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
      body: JSON.stringify(data),
      signal: controller.signal,
    })
      .then(async (res) => {
        if (!res.ok) {
          const body = await res.text().catch(() => '');
          throw new Error(`AI error: ${res.status} — ${body}`);
        }
        const reader = res.body?.getReader();
        if (!reader) throw new Error('No response body');

        const decoder = new TextDecoder();
        let buffer = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          // SSE format: "data: chunk\n\n"
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              onChunk(line.slice(6));
            }
          }
        }
        // Flush remaining buffer
        if (buffer.startsWith('data: ')) {
          onChunk(buffer.slice(6));
        }
        onDone();
      })
      .catch((err) => {
        if ((err as Error).name !== 'AbortError') {
          onError(err as Error);
        }
      });
    return controller;
  },

  generatePractice: (data: { chapter_slug: string; difficulty: number; count: number }) =>
    request<{ questions: PracticeQuestion[] }>('/ai/generate-practice', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // ── 进度 ──
  getProgressSummary: (subject?: string) =>
    request<ProgressSummary>(`/progress/summary${subject ? `?subject=${subject}` : ''}`),

  getProgressTree: (subject?: string) =>
    request<unknown>(`/progress/tree${subject ? `?subject=${subject}` : ''}`),

  getDiary: () =>
    request<Array<{ id: number; session_date: string; reflection: string }>>('/progress/diary'),

  // ── 管理 ──
  getSm2State: (userId?: number) =>
    request<{ target_user?: Record<string, unknown>; nodes: Array<Record<string, unknown>> }>(
      `/admin/sm2-state${userId ? `?user_id=${userId}` : ''}`,
    ),

  overrideSm2: (data: Record<string, unknown>) =>
    request<{ status: string }>('/admin/sm2-override', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  reloadContent: () =>
    request<{ status: string; nodes_loaded: number; questions_loaded: number }>(
      '/admin/reload-content',
      { method: 'POST' },
    ),

  updateConfig: (data: { param_path: string; new_value: string }) =>
    request<{ status: string }>('/admin/config-update', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // ── 用户管理 ──
  getUsers: (role?: string) =>
    request<{ users: Array<Record<string, unknown>>; total: number }>(
      `/admin/users${role ? `?role=${encodeURIComponent(role)}` : ''}`,
    ),

  getUserDetail: (userId: number) =>
    request<{ user: Record<string, unknown> }>(`/admin/users/${userId}`),

  updateUserRole: (userId: number, role: string) =>
    request<{ status: string }>(`/admin/users/${userId}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role }),
    }),

  resetUserPassword: (userId: number, newPassword: string) =>
    request<{ status: string; username: string }>(`/admin/users/${userId}/reset-password`, {
      method: 'POST',
      body: JSON.stringify({ new_password: newPassword }),
    }),

  deleteUser: (userId: number) =>
    request<{ status: string }>(`/admin/users/${userId}`, { method: 'DELETE' }),

  getUserProgress: (userId: number) =>
    request<{ user: Record<string, unknown>; nodes: Array<Record<string, unknown>> }>(
      `/admin/users/${userId}/progress`,
    ),

  // ── 聊天会话 ──
  getChatSessions: (chapterSlug: string) =>
    request<ChatSessionData[]>(`/chat/sessions?chapter_slug=${encodeURIComponent(chapterSlug)}`),

  createChatSession: (chapterSlug: string, title: string = '新对话') =>
    request<ChatSessionData>('/chat/sessions', {
      method: 'POST',
      body: JSON.stringify({ chapter_slug: chapterSlug, title }),
    }),

  deleteChatSession: (sessionId: number) =>
    request<{ status: string }>(`/chat/sessions/${sessionId}`, { method: 'DELETE' }),

  getChatMessages: (sessionId: number) =>
    request<AIMessage[]>(`/chat/sessions/${sessionId}/messages`),

  saveChatMessages: (sessionId: number, messages: AIMessage[]) =>
    request<{ status: string }>(`/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ messages }),
    }),

  // ── 考试 ──

  getExamList: (subject?: string) =>
    request<ExamListItem[]>(`/exam/list${subject ? `?subject=${subject}` : ''}`),

  getExam: (examId: number) =>
    request<ExamDetail>(`/exam/${examId}`),

  startExam: (examId: number) =>
    request<ExamAttemptData>(`/exam/${examId}/start`, { method: 'POST' }),

  submitExamAnswer: (examId: number, attemptId: number, questionId: number, answer: string) =>
    request<ExamAnswerResult>(`/exam/${examId}/answer`, {
      method: 'POST',
      body: JSON.stringify({ attempt_id: attemptId, question_id: questionId, answer }),
    }),

  finishExam: (examId: number, attemptId: number) =>
    request<ExamResultData>(`/exam/${examId}/finish?attempt_id=${attemptId}`, {
      method: 'POST',
    }),

  getExamResult: (examId: number, attemptId: number) =>
    request<ExamResultData>(`/exam/${examId}/result/${attemptId}`),

  generateExam: (data: {
    subject: string;
    chapter_slugs: string[];
    question_count: number;
    difficulty_level: string;
    title?: string;
    description?: string;
    time_limit_min?: number;
    passing_score?: number;
  }) =>
    request<{ exam_id: number; title: string; subject: string; question_count: number; status: string; error?: string }>(
      '/exam/generate',
      { method: 'POST', body: JSON.stringify(data) },
    ),

  getManageExamList: (subject?: string) =>
    request<ExamManageItem[]>(`/exam/manage/list${subject ? `?subject=${subject}` : ''}`),

  publishExam: (examId: number) =>
    request<{ status: string }>(`/exam/${examId}/publish`, { method: 'PUT' }),

  deleteExam: (examId: number) =>
    request<{ status: string }>(`/exam/${examId}`, { method: 'DELETE' }),

  getExamManageResults: (examId: number) =>
    request<{ exam_id: number; exam_title: string; total_attempts: number; avg_score: number; passing_score: number; results: ExamResultSummary[] }>(
      `/exam/manage/${examId}/results`,
    ),
};
