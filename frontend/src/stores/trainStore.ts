import { create } from 'zustand';
import type { SessionData, FeynmanResult } from '../types';
import { api } from '../api/client';

type StepStatus = 'pending' | 'active' | 'completed';

interface TrainState {
  subject: 'math' | 'english' | null;
  sessionData: SessionData | null;
  loading: boolean;
  error: string | null;
  currentStep: number;
  stepStatus: Record<number, StepStatus>;
  answers: Record<string, { answer: unknown; confidence: number }>;
  feynmanExplanation: string;
  feynmanDeepChoice: 'A' | 'B' | null;
  feynmanDeepAnswer: string;
  feynmanResult: FeynmanResult | null;
  confidence: number;
  thoughtDiary: string;
  sessionStartTime: number | null;

  setSubject: (s: 'math' | 'english') => void;
  fetchSession: () => Promise<void>;
  goToStep: (step: number) => void;
  submitAnswer: (qid: string, answer: unknown, confidence: number, stepType: 'warmup' | 'training') => Promise<void>;
  setFeynmanExplanation: (text: string) => void;
  setFeynmanDeepChoice: (choice: 'A' | 'B') => void;
  setFeynmanDeepAnswer: (text: string) => void;
  submitFeynman: () => Promise<void>;
  setConfidence: (v: number) => void;
  setThoughtDiary: (v: string) => void;
  submitCalibration: () => Promise<void>;
  completeSession: () => Promise<void>;
}

export const useTrainStore = create<TrainState>((set, get) => ({
  subject: null,
  sessionData: null,
  loading: false,
  error: null,
  currentStep: 1,
  stepStatus: { 1: 'active', 2: 'pending', 3: 'pending', 4: 'pending', 5: 'pending', 6: 'pending' },
  answers: {},
  feynmanExplanation: '',
  feynmanDeepChoice: null,
  feynmanDeepAnswer: '',
  feynmanResult: null,
  confidence: 0,
  thoughtDiary: '',
  sessionStartTime: null,

  setSubject: (s) => set({ subject: s }),

  fetchSession: async () => {
    const { subject } = get();
    set({ loading: true, error: null });
    try {
      const data = await api.getSessionToday(subject ?? undefined);
      set({ sessionData: data, sessionStartTime: Date.now(), loading: false });
    } catch (e: unknown) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  goToStep: (step: number) => {
    const status = { ...get().stepStatus };
    for (let s = 1; s < step; s++) {
      if (status[s] === 'active') status[s] = 'completed';
    }
    status[step] = 'active';
    set({ currentStep: step, stepStatus: status });
  },

  submitAnswer: async (qid, answer, confidence, stepType) => {
    const { sessionData } = get();
    if (!sessionData) return;
    try {
      await api.submitAnswer({
        session_id: sessionData.session_id,
        question_id: qid,
        step_type: stepType,
        user_answer: answer,
        confidence,
      });
      const answers = { ...get().answers };
      answers[qid] = { answer, confidence };
      set({ answers });
    } catch (e) {
      console.error('Submit answer failed:', e);
    }
  },

  setFeynmanExplanation: (text) => set({ feynmanExplanation: text }),
  setFeynmanDeepChoice: (choice) => set({ feynmanDeepChoice: choice }),
  setFeynmanDeepAnswer: (text) => set({ feynmanDeepAnswer: text }),

  submitFeynman: async () => {
    const { sessionData, feynmanExplanation, feynmanDeepChoice, feynmanDeepAnswer } = get();
    if (!sessionData) return;
    try {
      const result = await api.submitFeynman({
        session_id: sessionData.session_id,
        explanation: feynmanExplanation,
        deep_choice: feynmanDeepChoice ?? undefined,
        deep_answer: feynmanDeepAnswer || undefined,
      });
      set({ feynmanResult: result });
    } catch (e) {
      console.error('Submit feynman failed:', e);
    }
  },

  setConfidence: (v) => set({ confidence: v }),
  setThoughtDiary: (v) => set({ thoughtDiary: v }),

  submitCalibration: async () => {
    const { sessionData, confidence, thoughtDiary } = get();
    if (!sessionData) return;
    try {
      await api.submitCalibrate({
        session_id: sessionData.session_id,
        confidence,
        thought_diary: thoughtDiary,
      });
    } catch (e) {
      console.error('Submit calibration failed:', e);
    }
  },

  completeSession: async () => {
    const { sessionData, sessionStartTime } = get();
    if (!sessionData) return;
    const totalTime = sessionStartTime ? Math.floor((Date.now() - sessionStartTime) / 1000) : 0;
    try {
      await api.completeSession({ session_id: sessionData.session_id, total_time_sec: totalTime });
    } catch (e) {
      console.error('Complete session failed:', e);
    }
  },
}));
