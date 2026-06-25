import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  AnswerFeedback,
  AIMessage,
  ConceptData,
  ExampleData,
  PracticeQuestion,
  TestQuestion,
  SummaryData,
  ProgressSummary,
  ChatSessionData,
} from '../types';
import { api } from '../api/client';

export type Stage = 'concept' | 'examples' | 'practice' | 'test' | 'summary';

export interface QuestionResult {
  questionId: string;
  userAnswer: string;
  isCorrect: boolean | null;
  feedback: AnswerFeedback | null;
}

interface LearnState {
  // ── 章节状态 ──
  subject: 'math' | 'english' | null;
  chapterSlug: string | null;
  chapterTitle: string | null;
  currentStage: Stage;
  stageData: ConceptData | ExampleData[] | PracticeQuestion[] | TestQuestion[] | SummaryData | null;

  // ── 可用章节列表 ──
  availableChapters: ProgressSummary['nodes'];

  // ── 加载状态 ──
  loading: boolean;
  error: string | null;

  // ── 练习/测试状态 ──
  currentQuestionIndex: number;
  questionResults: Record<string, QuestionResult>;
  testCompleted: boolean;
  testScore: { correct: number; total: number } | null;

  // ── AI 侧边栏 ──
  aiOpen: boolean;
  aiMessages: AIMessage[];
  aiStreaming: boolean;
  aiPosition: string; // e.g. "例题 2/3" or "练习 第 3 题"

  // ── 聊天会话 ──
  chatSessions: ChatSessionData[];
  activeSessionId: number | null;

  // ── 操作 ──
  setSubject: (s: 'math' | 'english') => void;
  loadAvailableChapters: () => Promise<void>;
  loadChapter: (slug: string) => Promise<void>;
  loadStage: (stage: Stage) => Promise<void>;
  goToStage: (stage: Stage) => void;
  submitAnswer: (questionId: string, answer: string, difficulty?: number, layer?: string) => Promise<AnswerFeedback>;
  setCurrentQuestion: (index: number) => void;
  nextQuestion: () => void;
  prevQuestion: () => void;
  finishTest: () => void;
  resetTest: () => void;

  // AI 操作
  toggleAI: () => void;
  openAI: (position?: string) => void;
  closeAI: () => void;
  addAIMessage: (msg: AIMessage) => void;
  clearAIMessages: () => void;
  setAIStreaming: (v: boolean) => void;
  setAIPosition: (pos: string) => void;

  // 聊天会话操作
  loadSessions: () => Promise<void>;
  createSession: (title?: string) => Promise<number>;
  switchSession: (sessionId: number) => Promise<void>;
  deleteSession: (sessionId: number) => Promise<void>;
  syncMessages: () => Promise<void>;
}

export const useLearnStore = create<LearnState>()(
  persist(
    (set, get) => ({
      subject: null,
      chapterSlug: null,
      chapterTitle: null,
      currentStage: 'concept',
      stageData: null,
      availableChapters: [],
      loading: false,
      error: null,
      currentQuestionIndex: 0,
      questionResults: {},
      testCompleted: false,
      testScore: null,
      aiOpen: false,
      aiMessages: [],
      aiStreaming: false,
      aiPosition: '',
      chatSessions: [],
      activeSessionId: null,

      // ── Subject ──
      setSubject: (s) => set({ subject: s }),

      // ── Load chapters list ──
      loadAvailableChapters: async () => {
        const { subject } = get();
        if (!subject) return;
        set({ loading: true, error: null });
        try {
          const summary = await api.getProgressSummary(subject);
          set({
            availableChapters: summary.nodes,
            loading: false,
          });
        } catch (e: unknown) {
          set({ error: (e as Error).message, loading: false });
        }
      },

      // ── Load chapter ──
      loadChapter: async (slug: string) => {
        // Only reset if switching to a different chapter
        const { chapterSlug: prevSlug } = get();
        const switchingChapter = prevSlug !== slug;
        set({
          loading: true,
          error: null,
          chapterSlug: slug,
          ...(switchingChapter ? { currentStage: 'concept', questionResults: {}, testCompleted: false, testScore: null, aiMessages: [] } : {}),
        });
        try {
          await get().loadStage('concept');
          get().loadAvailableChapters();
        } catch (e: unknown) {
          set({ error: (e as Error).message, loading: false });
        }
      },

      // ── Load stage data ──
      loadStage: async (stage: Stage) => {
        const { chapterSlug } = get();
        if (!chapterSlug) return;
        set({ loading: true, error: null, currentStage: stage, currentQuestionIndex: 0 });
        try {
          const result = await api.getChapter(chapterSlug, stage);
          set({
            chapterTitle: result.title,
            stageData: result.data,
            loading: false,
          });
        } catch (e: unknown) {
          set({ error: (e as Error).message, loading: false });
        }
      },

      goToStage: (stage: Stage) => {
        get().loadStage(stage);
      },

      // ── Submit answer ──
      submitAnswer: async (questionId, answer, difficulty, layer) => {
        const { chapterSlug } = get();
        if (!chapterSlug) throw new Error('No chapter loaded');

        const feedback = await api.submitAnswer({
          chapter_slug: chapterSlug,
          question_id: questionId,
          user_answer: answer,
          difficulty,
          layer,
        });

        const results = { ...get().questionResults };
        results[questionId] = {
          questionId,
          userAnswer: answer,
          isCorrect: feedback.is_correct,
          feedback,
        };
        set({ questionResults: results });

        return feedback;
      },

      setCurrentQuestion: (index) => set({ currentQuestionIndex: index }),

      nextQuestion: () => {
        const { currentQuestionIndex, stageData, currentStage } = get();
        const questions = (currentStage === 'practice' || currentStage === 'test')
          ? (stageData as PracticeQuestion[] | TestQuestion[])
          : [];
        if (currentQuestionIndex < questions.length - 1) {
          set({ currentQuestionIndex: currentQuestionIndex + 1 });
        }
      },

      prevQuestion: () => {
        const { currentQuestionIndex } = get();
        if (currentQuestionIndex > 0) {
          set({ currentQuestionIndex: currentQuestionIndex - 1 });
        }
      },

      finishTest: () => {
        const { questionResults, stageData, currentStage } = get();
        if (currentStage !== 'test') return;
        const questions = (stageData as TestQuestion[]) || [];
        let correct = 0;
        for (const q of questions) {
          const r = questionResults[q.id];
          if (r?.isCorrect === true) correct++;
        }
        set({ testCompleted: true, testScore: { correct, total: questions.length } });
      },

      resetTest: () => {
        set({ questionResults: {}, currentQuestionIndex: 0, testCompleted: false, testScore: null });
      },

      // ── AI ──
      toggleAI: () => set((s) => ({ aiOpen: !s.aiOpen })),
      openAI: (position) => {
        const state = get();
        set({
          aiOpen: true,
          aiPosition: position || state.aiPosition,
        });
      },
      closeAI: () => set({ aiOpen: false }),
      addAIMessage: (msg) => set((s) => ({ aiMessages: [...s.aiMessages, msg] })),
      clearAIMessages: () => set({ aiMessages: [] }),
      setAIStreaming: (v) => set({ aiStreaming: v }),
      setAIPosition: (pos) => set({ aiPosition: pos }),

      // ── 聊天会话操作 ──
      loadSessions: async () => {
        const { chapterSlug } = get();
        if (!chapterSlug) return;
        try {
          const sessions = await api.getChatSessions(chapterSlug);
          set({ chatSessions: sessions });
        } catch {
          // 静默失败
        }
      },

      createSession: async (title = '新对话') => {
        const { chapterSlug } = get();
        if (!chapterSlug) throw new Error('No chapter');
        const session = await api.createChatSession(chapterSlug, title);
        set((s) => ({
          chatSessions: [session, ...s.chatSessions],
          activeSessionId: session.id,
          aiMessages: [],
        }));
        return session.id;
      },

      switchSession: async (sessionId) => {
        set({ activeSessionId: sessionId, aiMessages: [], aiStreaming: false });
        try {
          const messages = await api.getChatMessages(sessionId);
          const formatted: AIMessage[] = messages.map((m: { role: string; content: string }) => ({
            role: m.role as 'user' | 'assistant',
            content: m.content,
          }));
          set({ aiMessages: formatted });
        } catch {
          // 加载失败保持空列表
        }
      },

      deleteSession: async (sessionId) => {
        await api.deleteChatSession(sessionId);
        const state = get();
        const sessions = state.chatSessions.filter((s) => s.id !== sessionId);
        const updates: Partial<LearnState> = { chatSessions: sessions };
        if (state.activeSessionId === sessionId) {
          updates.activeSessionId = null;
          updates.aiMessages = [];
        }
        set(updates);
      },

      syncMessages: async () => {
        const { activeSessionId, aiMessages } = get();
        if (!activeSessionId) return;
        const nonEmpty = aiMessages.filter((m) => m.content);
        if (nonEmpty.length === 0) return;
        try {
          await api.saveChatMessages(activeSessionId, nonEmpty);
          // 刷新会话列表以更新时间/标题
          get().loadSessions();
        } catch {
          // 静默失败
        }
      },
    }),
    {
      name: 'learn-store',
      partialize: (state) => ({
        subject: state.subject,
        chapterSlug: state.chapterSlug,
        chapterTitle: state.chapterTitle,
        currentStage: state.currentStage,
        availableChapters: state.availableChapters,
        currentQuestionIndex: state.currentQuestionIndex,
        questionResults: state.questionResults,
        testCompleted: state.testCompleted,
        testScore: state.testScore,
        activeSessionId: state.activeSessionId,
      }),
    }
  )
);
