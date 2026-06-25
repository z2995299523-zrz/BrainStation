// ============================================================
// 章节学习类型（Phase 5-8 重构）
// ============================================================

export interface ChapterContent {
  slug: string;
  title: string;
  subject: string;
  stage: string;
  data: ConceptData | ExampleData[] | PracticeQuestion[] | TestQuestion[] | SummaryData;
}

export interface ConceptData {
  summary: string;
  sections: ConceptSection[];
}

export interface ConceptSection {
  title: string;
  content: string;
}

export interface ExampleData {
  title: string;
  problem: string;
  steps: string[];
  answer: string;
}

export interface PracticeQuestion {
  id: string;
  stem: string;
  answer: string;
  hints?: string[];
  explanation?: string;
  q_type?: 'choice' | 'fill';
  options?: string[];
}

export interface TestQuestion {
  id: string;
  stem: string;
  answer: string;
  difficulty: number;
  layer: string;
  explanation?: string;
  q_type?: 'choice' | 'fill';
  options?: string[];
}

export interface SummaryData {
  chapter_title: string;
  key_points: string[];
  message: string;
}

// ============================================================
// 答题反馈
// ============================================================

export interface AnswerFeedback {
  is_correct: boolean | null;
  correct_answer: string;
  explanation: string;
  hints: string[];
  mastery_update: MasteryUpdate;
}

export interface MasteryUpdate {
  node_slug: string;
  mastery_before: number;
  mastery_after: number;
  new_ef: number;
  new_interval: number;
  next_review_at: string | null;
}

// ============================================================
// AI 对话
// ============================================================

export interface AIMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatSessionData {
  id: number;
  chapter_slug: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface AIAskRequest {
  chapter_slug: string;
  current_stage: string;
  current_position: string;
  question: string;
}

export interface GeneratePracticeRequest {
  chapter_slug: string;
  difficulty: number;
  count: number;
}

export interface GeneratePracticeResponse {
  questions: PracticeQuestion[];
}

// ============================================================
// 保留的现有类型（兼容旧代码）
// ============================================================

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
    trigger: { type: string; title: string; content: { text: string; media_url: string | null; question: string } };
    learn: LearnData;
    checkup: { questions: Question[] };
    exam: { questions: Question[] };
    feynman: FeynmanData;
    calibration: { confidence_prompt: string; thought_card: string };
  };
  phases?: {
    learn: string[];
    test: string[];
  };
}

export type InteractionType = 'drag-sort' | 'match-pairs' | 'click-reveal' | 'fill-blanks' | 'self-check';

export interface DragItem {
  id: string;
  label: string;
  correct_category: string;
  [key: string]: unknown;
}

export interface DragCategory {
  id: string;
  label: string;
}

export interface DragSortConfig {
  items: DragItem[];
  categories: DragCategory[];
  drag_style: 'categorize' | 'sequence';
}

export interface MatchPair {
  left: string;
  right: string;
}

export interface MatchPairsConfig {
  pairs: MatchPair[];
  match_style: 'lines' | 'tap' | 'select';
}

export interface RevealStep {
  prompt: string;
  reveal: string;
  explanation: string;
}

export interface ClickRevealConfig {
  steps: RevealStep[];
}

export interface FillBlank {
  answer: string;
  hint?: string;
}

export interface FillBlanksConfig {
  context: string;
  blanks: FillBlank[];
  feedback_on_submit?: boolean;
}

export interface CheckQuestion {
  stem: string;
  type: 'choice' | 'fill';
  options?: string[];
  correct: number | string;
  explanation: string;
}

export interface SelfCheckConfig {
  questions: CheckQuestion[];
}

export interface InteractiveDef {
  id: string;
  unit: string;
  type: InteractionType;
  title: string;
  instruction: string;
  config: DragSortConfig | MatchPairsConfig | ClickRevealConfig | FillBlanksConfig | SelfCheckConfig;
}

export interface MicroUnit {
  id: string;
  title: string;
  text: string;
}

export interface LayerContent {
  units?: MicroUnit[];
  text?: string;
  highlights?: string[];
  thought_seeds?: string[];
  spoken_examples?: Array<{ text: string; label: string }>;
  word_groups?: Array<{
    title: string;
    words: Array<{ word: string; ipa: string; zh: string; speak: string }>;
  }>;
  phonemes?: Record<string, Array<{
    symbol: string;
    speak_phoneme: string;
    word: string;
    word_ipa: string;
    speak_word: string;
  }>>;
  examples?: Array<Record<string, unknown>>;
  [key: string]: unknown;
}

export interface LearnData {
  node_title: string;
  subject: string;
  operation: LayerContent;
  understand: LayerContent;
  connect: LayerContent;
  interactives?: InteractiveDef[];
}

export interface TreeNodeData {
  slug: string;
  title: string;
  status: string;
  mastery: number;
  prerequisites: string[];
  children?: TreeNodeData[];
}

export interface ProgressTree {
  tree: Record<string, TreeNodeData[]>;
  unlocked_nodes: string[];
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
  prerequisites?: string[];
}

// ============================================================
// 考试模块
// ============================================================

export interface ExamListItem {
  id: number;
  title: string;
  description: string;
  subject: 'math' | 'english';
  chapters: string[];
  question_count: number;
  time_limit_min: number;
  difficulty_level: string;
  passing_score: number;
  last_score: number | null;
  attempts_count: number;
  created_at: string;
}

export interface ExamDetail {
  id: number;
  title: string;
  description: string;
  subject: string;
  status: string;
  chapters: string[];
  question_count: number;
  time_limit_min: number;
  difficulty_level: string;
  passing_score: number;
  questions: ExamQuestionData[];
}

export interface ExamQuestionData {
  id: number;
  question_index: number;
  stem: string;
  options: string[] | null;
  difficulty: number;
  q_type: 'choice' | 'fill';
  chapter_slug: string;
}

export interface ExamAttemptData {
  attempt_id: number;
  status: string;
  total_questions: number;
  started_at: string;
}

export interface ExamAnswerResult {
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
}

export interface ExamResultData {
  attempt_id: number;
  exam_id: number;
  exam_title: string;
  status: string;
  score: number | null;
  total_questions: number;
  correct_count: number;
  passed: boolean;
  passing_score: number;
  weak_areas: WeakArea[];
  answers: ExamAnswerDetail[];
  time_spent_sec: number | null;
  started_at: string;
  completed_at: string | null;
}

export interface ExamAnswerDetail {
  question_id: number;
  user_answer: string;
  is_correct: boolean;
  stem: string;
  correct_answer: string;
  explanation: string;
  options: string[] | null;
  q_type: string;
  chapter_slug: string;
}

export interface WeakArea {
  chapter_slug: string;
  chapter_title: string;
  error_count: number;
  total_count: number;
  accuracy: number;
}

export interface ExamManageItem {
  id: number;
  title: string;
  description: string;
  subject: string;
  status: string;
  chapters: string[];
  question_count: number;
  time_limit_min: number;
  difficulty_level: string;
  passing_score: number;
  attempt_count: number;
  created_at: string;
  updated_at: string;
}

export interface ExamResultSummary {
  attempt_id: number;
  username: string;
  score: number | null;
  correct_count: number;
  total_questions: number;
  passed: boolean;
  time_spent_sec: number | null;
  completed_at: string;
}

// ── 用户管理 ──

export interface UserManageItem {
  id: number;
  username: string;
  role: 'learner' | 'examiner' | 'admin';
  created_at: string;
  progress_count: number;
  mastered_count: number;
  exam_count: number;
}
