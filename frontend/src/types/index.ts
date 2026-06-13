export interface Question {
  id: string;
  node_slug: string;
  subject: 'math' | 'english';
  layer: 'operation' | 'understand' | 'connect';
  q_type: 'choice' | 'fill' | 'open' | 'explain';
  difficulty: number;
  content: {
    stem: string;
    options?: string[];
    images?: string[];
  };
  variants?: Array<{
    stem: string;
    options?: string[];
    answer_correct?: number;
  }>;
  answer?: {
    correct?: number | string;
    explanation?: string;
    rubric?: string;
    example?: string;
  };
}

export interface FeynmanData {
  base_prompt: string;
  deep_questions: [string, string];
  key_elements: string[];
  missing_hints: Record<string, string>;
}

export interface FeynmanResult {
  quality_flag: 'excellent' | 'good' | 'needs_work';
  feedback: string;
  completeness: number;
  matched: string[];
  missing: string[];
}

export interface SessionData {
  session_id: number;
  session_date: string;
  day_number: number;
  status: string;
  target_node: {
    slug: string;
    title: string;
    subject: string;
    tier: string;
  } | null;
  steps: {
    warmup: { questions: Question[] };
    trigger: { type: string; title: string; content: { text: string; media_url: string | null; question: string } };
    learn: { node_title: string; subject: string; operation: Record<string, unknown>; understand: Record<string, unknown>; connect: Record<string, unknown> };
    training: { questions: Question[] };
    feynman: FeynmanData;
    calibration: { confidence_prompt: string; thought_card: string };
  };
}

export interface ProgressSummary {
  total_nodes: number;
  mastered_nodes: number;
  learning_nodes: number;
  unlocked_nodes: number;
  locked_nodes: number;
  streak_days: number;
  total_sessions: number;
  total_attempts: number;
  overall_accuracy: number;
  nodes: NodeProgress[];
}

export interface NodeProgress {
  slug: string;
  title: string;
  subject: string;
  tier: string;
  status: string;
  mastery_level: number;
  ef: number;
  next_review_at: string | null;
}
