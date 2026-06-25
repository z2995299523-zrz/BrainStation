import { create } from 'zustand';
import type {
  ExamListItem,
  ExamDetail,
  ExamAttemptData,
  ExamAnswerResult,
  ExamResultData,
  ExamManageItem,
  ExamResultSummary,
} from '../types';
import { api } from '../api/client';

interface ExamState {
  // ── 考试列表 ──
  exams: ExamListItem[];
  manageExams: ExamManageItem[];
  loading: boolean;
  error: string | null;

  // ── 当前考试 ──
  currentExam: ExamDetail | null;
  currentAttempt: ExamAttemptData | null;
  currentQuestionIndex: number;
  answers: Record<number, { answer: string; result?: ExamAnswerResult }>;

  // ── 结果 ──
  result: ExamResultData | null;

  // ── 管理端 ──
  manageResults: { exam_id: number; exam_title: string; total_attempts: number; avg_score: number; passing_score: number; results: ExamResultSummary[] } | null;

  // ── 操作 ──
  loadExams: (subject?: string) => Promise<void>;
  loadManageExams: (subject?: string) => Promise<void>;
  loadExam: (examId: number) => Promise<void>;
  startExam: (examId: number) => Promise<void>;
  submitAnswer: (questionId: number, answer: string) => Promise<ExamAnswerResult>;
  goToQuestion: (index: number) => void;
  finishExam: () => Promise<void>;
  loadResult: (examId: number, attemptId: number) => Promise<void>;
  generateExam: (data: Parameters<typeof api.generateExam>[0]) => Promise<{ exam_id: number; error?: string }>;
  publishExam: (examId: number) => Promise<void>;
  deleteExam: (examId: number) => Promise<void>;
  loadManageResults: (examId: number) => Promise<void>;
  resetExam: () => void;
}

export const useExamStore = create<ExamState>()((set, get) => ({
  exams: [],
  manageExams: [],
  loading: false,
  error: null,
  currentExam: null,
  currentAttempt: null,
  currentQuestionIndex: 0,
  answers: {},
  result: null,
  manageResults: null,

  loadExams: async (subject) => {
    set({ loading: true, error: null });
    try {
      const exams = await api.getExamList(subject);
      set({ exams, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  loadManageExams: async (subject) => {
    set({ loading: true, error: null });
    try {
      const manageExams = await api.getManageExamList(subject);
      set({ manageExams, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  loadExam: async (examId) => {
    set({ loading: true, error: null });
    try {
      const currentExam = await api.getExam(examId);
      set({
        currentExam,
        currentQuestionIndex: 0,
        answers: {},
        result: null,
        loading: false,
      });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  startExam: async (examId) => {
    set({ loading: true, error: null });
    try {
      const currentAttempt = await api.startExam(examId);
      set({ currentAttempt, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  submitAnswer: async (questionId, answer) => {
    const { currentExam, currentAttempt } = get();
    if (!currentExam || !currentAttempt) throw new Error('No active exam');

    const result = await api.submitExamAnswer(
      currentExam.id,
      currentAttempt.attempt_id,
      questionId,
      answer,
    );

    const answers = { ...get().answers };
    answers[questionId] = { answer, result };
    set({ answers });

    return result;
  },

  goToQuestion: (index) => {
    set({ currentQuestionIndex: index });
  },

  finishExam: async () => {
    const { currentExam, currentAttempt } = get();
    if (!currentExam || !currentAttempt) return;

    set({ loading: true });
    try {
      const result = await api.finishExam(currentExam.id, currentAttempt.attempt_id);
      set({ result, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  loadResult: async (examId, attemptId) => {
    set({ loading: true, error: null });
    try {
      const result = await api.getExamResult(examId, attemptId);
      set({ result, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  generateExam: async (data) => {
    set({ loading: true, error: null });
    try {
      const result = await api.generateExam(data);
      set({ loading: false });
      return result;
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
      throw e;
    }
  },

  publishExam: async (examId) => {
    await api.publishExam(examId);
    get().loadManageExams();
  },

  deleteExam: async (examId) => {
    await api.deleteExam(examId);
    get().loadManageExams();
  },

  loadManageResults: async (examId) => {
    set({ loading: true, error: null });
    try {
      const manageResults = await api.getExamManageResults(examId);
      set({ manageResults, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  resetExam: () => {
    set({
      currentExam: null,
      currentAttempt: null,
      currentQuestionIndex: 0,
      answers: {},
      result: null,
    });
  },
}));
