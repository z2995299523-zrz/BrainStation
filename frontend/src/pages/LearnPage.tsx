import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useLearnStore, type Stage } from '../stores/learnStore';
import AISidebar from '../components/ai/AISidebar';
import { renderMarkdown } from '../utils/renderMarkdown';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Card, CardContent } from '../components/ui/card';
import { toast } from 'sonner';
import type {
  ConceptData,
  ConceptSection,
  ExampleData,
  PracticeQuestion,
  TestQuestion,
  SummaryData,
} from '../types';

// ════════════════════════════════════════════════════════════
// 阶段指示器（Stepper 样式）
// ════════════════════════════════════════════════════════════

const STAGES: { key: Stage; label: string; num: string }[] = [
  { key: 'concept', label: '概念', num: '1' },
  { key: 'examples', label: '例题', num: '2' },
  { key: 'practice', label: '练习', num: '3' },
  { key: 'test', label: '测试', num: '4' },
  { key: 'summary', label: '总结', num: '5' },
];

function StageIndicator({
  current,
  onSelect,
  isMath,
}: {
  current: Stage;
  onSelect: (s: Stage) => void;
  isMath: boolean;
}) {
  const currentIdx = STAGES.findIndex((s) => s.key === current);
  const activeColor = isMath ? 'bg-blue-600' : 'bg-emerald-600';

  return (
    <div className="flex items-center justify-center mb-6">
      {STAGES.map((s, i) => {
        const isActive = s.key === current;
        const isPast = i < currentIdx;
        const isFuture = i > currentIdx;

        return (
          <div key={s.key} className="flex items-center">
            {/* Step circle + label */}
            <button
              onClick={() => onSelect(s.key)}
              disabled={isFuture}
              className="flex flex-col items-center gap-1 group"
            >
              <span
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                  isPast
                    ? 'bg-green-500 text-white'
                    : isActive
                    ? `${activeColor} text-white shadow-md scale-110`
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500'
                } ${isFuture ? 'cursor-not-allowed' : 'cursor-pointer hover:scale-105'}`}
              >
                {isPast ? '✓' : s.num}
              </span>
              <span
                className={`text-xs transition-colors hidden sm:block ${
                  isActive
                    ? 'text-gray-800 dark:text-gray-200 font-medium'
                    : isPast
                    ? 'text-green-600 dark:text-green-400'
                    : 'text-gray-400 dark:text-gray-500'
                }`}
              >
                {s.label}
              </span>
            </button>
            {/* Connector line */}
            {i < STAGES.length - 1 && (
              <div
                className={`h-0.5 w-6 sm:w-10 mx-1 mt-[-0.75rem] ${
                  i < currentIdx ? 'bg-green-400' : 'bg-gray-200 dark:bg-gray-700'
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

// ════════════════════════════════════════════════════════════
// 概念阶段
// ════════════════════════════════════════════════════════════

function ConceptStage({ data, accentColor, onNextStage }: { data: ConceptData; accentColor: string; onNextStage: () => void }) {
  const [pageIndex, setPageIndex] = useState(0);
  const sections = data.sections || [];
  const totalPages = sections.length + 1; // +1 for summary page
  const isLastPage = pageIndex === totalPages - 1;

  const currentSection: ConceptSection | null =
    pageIndex === 0 ? null : sections[pageIndex - 1];

  return (
    <div>
      {/* Summary page */}
      {pageIndex === 0 && (
        <div className={`rounded-xl border-l-4 ${accentColor.replace('bg-', 'border-').replace('text-', 'border-')} bg-white dark:bg-gray-800 p-5 shadow-sm`}>
          <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-3">📖 章节概览</h3>
          <p
            className="text-gray-600 dark:text-gray-400 leading-relaxed"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(data.summary) }}
          />
          {sections.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
              <p className="text-sm text-gray-500 mb-2">本章包含 {sections.length} 个知识点：</p>
              <ul className="space-y-1">
                {sections.map((s, i) => (
                  <li key={i} className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                    <span className={`w-6 h-6 rounded-full ${accentColor} text-white text-xs flex items-center justify-center shrink-0`}>
                      {i + 1}
                    </span>
                    <span dangerouslySetInnerHTML={{ __html: renderMarkdown(s.title) }} />
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Section page */}
      {currentSection && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm">
          <h3
            className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(currentSection.title) }}
          />
          <div
            className="prose prose-sm dark:prose-invert max-w-none leading-relaxed text-gray-700 dark:text-gray-300"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(currentSection.content) }}
          />
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-between items-center mt-6">
          <Button
            variant="outline"
            onClick={() => setPageIndex(Math.max(0, pageIndex - 1))}
            disabled={pageIndex === 0}
          >
            ← 上一页
          </Button>
          <span className="text-sm text-muted-foreground font-medium">
            {pageIndex + 1} / {totalPages}
          </span>
          {isLastPage ? (
            <Button onClick={onNextStage} className={accentColor}>
              进入例题 →
            </Button>
          ) : (
            <Button onClick={() => setPageIndex(Math.min(totalPages - 1, pageIndex + 1))} className={accentColor}>
              下一页 →
            </Button>
          )}
        </div>
      )}

      {/* No sections - direct next stage button */}
      {totalPages <= 1 && (
        <div className="flex justify-center mt-6">
          <Button onClick={onNextStage} size="lg" className={accentColor}>
            进入例题 →
          </Button>
        </div>
      )}
    </div>
  );
}

// ════════════════════════════════════════════════════════════
// 例题阶段
// ════════════════════════════════════════════════════════════

function ExampleStage({
  data,
  accentColor,
  onAIOpen,
  onNextStage,
}: {
  data: ExampleData[];
  accentColor: string;
  onAIOpen: (position: string) => void;
  onNextStage: () => void;
}) {
  const [exampleIndex, setExampleIndex] = useState(0);
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set());
  const example = data[exampleIndex];
  const isLastExample = exampleIndex === data.length - 1;

  if (!example) return <p className="text-gray-500 text-center py-8">暂无例题</p>;

  const toggleStep = (i: number) => {
    const next = new Set(expandedSteps);
    if (next.has(i)) next.delete(i);
    else next.add(i);
    setExpandedSteps(next);
  };

  const expandAll = () => setExpandedSteps(new Set(example.steps.map((_, i) => i)));

  return (
    <div>
      {/* Example Card */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm mb-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-bold text-gray-800 dark:text-gray-200">
            💡 {example.title}
          </h3>
          <button
            onClick={() => onAIOpen(`例题 ${exampleIndex + 1}/${data.length}`)}
            className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
            title="问 AI 导师"
          >
            💬
          </button>
        </div>

        <div
          className={`rounded-lg p-4 mb-3 text-lg text-center border-2 ${accentColor.replace('bg-', 'border-').replace('text-', 'border-')}/30 bg-gray-50 dark:bg-gray-900`}
          dangerouslySetInnerHTML={{ __html: renderMarkdown(example.problem) }}
        />

        {/* Steps */}
        <div className="space-y-2">
          {example.steps.map((step, i) => (
            <div key={i} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleStep(i)}
                className="w-full flex items-center justify-between px-4 py-2.5 text-left text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
              >
                <span dangerouslySetInnerHTML={{ __html: `${expandedSteps.has(i) ? '▼' : '▶'} ${renderMarkdown(step)}` }} />
              </button>
              {expandedSteps.has(i) && (
                <div
                  className="px-4 pb-3 text-sm text-gray-600 dark:text-gray-400 border-t border-gray-100 dark:border-gray-700 pt-2"
                  dangerouslySetInnerHTML={{ __html: renderMarkdown(step) }}
                />
              )}
            </div>
          ))}
        </div>

        {example.steps.length > 0 && (
          <button onClick={expandAll} className="mt-3 text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400">
            全部展开
          </button>
        )}

        {/* Answer reveal */}
        {example.answer && (
          <div className="mt-4 p-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
            <p
              className="text-sm font-medium text-green-800 dark:text-green-300"
              dangerouslySetInnerHTML={{ __html: `✅ 答案：${renderMarkdown(example.answer)}` }}
            />
          </div>
        )}
      </div>

      {/* Example navigation */}
      {(data.length > 1 || isLastExample) && (
        <div className="flex justify-between items-center mt-6">
          <Button
            variant="outline"
            onClick={() => {
              setExampleIndex(Math.max(0, exampleIndex - 1));
              setExpandedSteps(new Set());
            }}
            disabled={exampleIndex === 0}
          >
            ← 上一题
          </Button>
          <span className="text-sm text-muted-foreground font-medium">
            例题 {exampleIndex + 1} / {data.length}
          </span>
          {isLastExample ? (
            <Button onClick={onNextStage} className={accentColor}>
              进入练习 →
            </Button>
          ) : (
            <Button
              onClick={() => {
                setExampleIndex(Math.min(data.length - 1, exampleIndex + 1));
                setExpandedSteps(new Set());
              }}
              className={accentColor}
            >
              下一题 →
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

// ════════════════════════════════════════════════════════════
// 选择题输入组件 (shadcn RadioGroup)
// ════════════════════════════════════════════════════════════

function ChoiceInput({
  options,
  isMath,
  disabled,
  onSelect,
}: {
  options: string[];
  isMath: boolean;
  disabled: boolean;
  onSelect: (letter: string) => void;
}) {
  const [value, setValue] = useState('');

  const handleValueChange = (v: string) => {
    if (disabled) return;
    setValue(v);
    onSelect(v);
  };

  return (
    <RadioGroup value={value} onValueChange={handleValueChange} className="space-y-2">
      {options.map((option, i) => {
        const letter = option.trim().charAt(0).toUpperCase();
        const label = option.slice(1).replace(/^[：:\.\、\)）]\s*/, '').trim();
        const isSelected = value === letter;
        return (
          <label
            key={i}
            className={`flex items-center gap-3 w-full px-4 py-3 rounded-lg border-2 transition-all ${
              isSelected
                ? `${isMath ? 'border-blue-500' : 'border-emerald-500'} bg-blue-50 dark:bg-blue-900/20`
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            } ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <RadioGroupItem value={letter} disabled={disabled} />
            <span
              className="text-sm text-gray-700 dark:text-gray-300"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(label) }}
            />
          </label>
        );
      })}
    </RadioGroup>
  );
}

// ════════════════════════════════════════════════════════════
// 练习阶段
// ════════════════════════════════════════════════════════════

function PracticeStage({
  data,
  accentColor,
  onAIOpen,
  onNextStage,
}: {
  data: PracticeQuestion[];
  chapterSlug: string;
  accentColor: string;
  onAIOpen: (position: string) => void;
  onNextStage: () => void;
}) {
  const questionResults = useLearnStore((s) => s.questionResults);
  const submitAnswer = useLearnStore((s) => s.submitAnswer);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const question = data[currentIdx];
  if (!question) return <p className="text-gray-500 text-center py-8">暂无练习题</p>;

  const result = questionResults[question.id];
  const hasSubmitted = !!result;
  const isLastQuestion = currentIdx === data.length - 1;
  const allAnswered = data.every((q) => !!questionResults[q.id]);

  const isChoice = question.q_type === 'choice';

  const handleSubmit = async () => {
    if (!userAnswer.trim() || submitting || hasSubmitted) return;
    setSubmitting(true);
    try {
      const feedback = await submitAnswer(question.id, userAnswer.trim());
      if (feedback.is_correct) {
        toast.success('✅ 回答正确！');
      } else {
        toast.error('❌ 回答错误', {
          description: feedback.correct_answer ? `正确答案：${feedback.correct_answer}` : undefined,
        });
      }
    } catch (e) {
      toast.error('提交失败，请重试');
    }
    setSubmitting(false);
  };

  const handleChoiceSelect = (letter: string) => {
    setUserAnswer(letter);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSubmit();
  };

  return (
    <div>
      <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm text-gray-500">
            第 {currentIdx + 1} 题 / 共 {data.length} 题
          </span>
          <button
            onClick={() => onAIOpen(`练习 第 ${currentIdx + 1} 题`)}
            className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
            title="问 AI 导师"
          >
            💬 有疑问？
          </button>
        </div>

        {/* Question stem */}
        <div className={`rounded-lg p-4 mb-4 text-lg text-center border-2 ${accentColor.replace('bg-', 'border-').replace('text-', 'border-')}/30 bg-gray-50 dark:bg-gray-900`}>
          <div dangerouslySetInnerHTML={{ __html: renderMarkdown(question.stem) }} />
        </div>

        {/* Answer input */}
        {!hasSubmitted ? (
          <div>
            {isChoice && question.options ? (
              <div className="space-y-3">
                <ChoiceInput
                  options={question.options}
                  isMath={accentColor === 'bg-blue-600'}
                  disabled={false}
                  onSelect={handleChoiceSelect}
                />
                <button
                  onClick={handleSubmit}
                  disabled={submitting || !userAnswer.trim()}
                  className={`w-full px-6 py-3 rounded-lg font-bold text-white transition-colors disabled:opacity-50 ${accentColor}`}
                >
                  {submitting ? '提交中...' : '提交答案'}
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <Input
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="输入你的答案..."
                  disabled={submitting}
                  className="flex-1 h-12 text-base"
                  autoFocus
                />
                <Button
                  onClick={handleSubmit}
                  disabled={submitting || !userAnswer.trim()}
                  className={accentColor}
                >
                  {submitting ? '提交中...' : '提交'}
                </Button>
              </div>
            )}
          </div>
        ) : (
          /* Feedback */
          <div className={`rounded-lg p-4 border-2 ${
            result.isCorrect === true
              ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
              : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
          }`}>
            <p className={`font-bold text-lg mb-2 ${
              result.isCorrect === true ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'
            }`}>
              {result.isCorrect === true ? '✅ 正确！' : '❌ 不对哦'}
            </p>
            {result.isCorrect === false && (
              <>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  你的答案：<span className="line-through text-red-500">{result.userAnswer}</span>
                </p>
                <p
                  className="text-sm text-gray-600 dark:text-gray-400 mb-3"
                  dangerouslySetInnerHTML={{ __html: `正确答案：<span class="font-bold text-green-600 dark:text-green-400">${renderMarkdown(result.feedback?.correct_answer || '')}</span>` }}
                />
                {result.feedback?.explanation && (
                  <p
                    className="text-sm text-gray-700 dark:text-gray-300 bg-white/50 dark:bg-gray-800/50 rounded p-3 mt-2"
                    dangerouslySetInnerHTML={{ __html: `💡 ${renderMarkdown(result.feedback.explanation)}` }}
                  />
                )}
                {result.feedback?.hints && result.feedback.hints.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {result.feedback.hints.map((h, i) => (
                      <p key={i} className="text-xs text-gray-500" dangerouslySetInnerHTML={{ __html: `💭 ${renderMarkdown(h)}` }} />
                    ))}
                  </div>
                )}
              </>
            )}
            {result.isCorrect === true && result.feedback?.explanation && (
              <p
                className="text-sm text-gray-700 dark:text-gray-300 bg-white/50 dark:bg-gray-800/50 rounded p-3 mt-2"
                dangerouslySetInnerHTML={{ __html: `💡 ${renderMarkdown(result.feedback.explanation)}` }}
              />
            )}
            {result.isCorrect === false && (
              <button
                onClick={() => onAIOpen(`练习 第 ${currentIdx + 1} 题（答错）`)}
                className="mt-3 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
              >
                💬 还是不理解？问问 AI 导师
              </button>
            )}
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center mt-4">
        <button
          onClick={() => {
            setCurrentIdx(Math.max(0, currentIdx - 1));
            setUserAnswer('');
          }}
          disabled={currentIdx === 0}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            currentIdx === 0
              ? 'bg-gray-100 dark:bg-gray-800 text-gray-400 cursor-not-allowed'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300'
          }`}
        >
          ← 上一题
        </button>
        <div className="flex items-center gap-2">
          {hasSubmitted && !isLastQuestion && (
            <button
              onClick={() => {
                const next = Math.min(data.length - 1, currentIdx + 1);
                setCurrentIdx(next);
                setUserAnswer('');
              }}
              className={`px-4 py-2 rounded-lg text-sm font-medium text-white ${accentColor}`}
            >
              下一题 →
            </button>
          )}
          {isLastQuestion && allAnswered && (
            <button
              onClick={onNextStage}
              className={`px-4 py-2 rounded-lg text-sm font-bold text-white transition-colors hover:opacity-90 ${accentColor}`}
            >
              进入测试 →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════════
// 测试阶段
// ════════════════════════════════════════════════════════════

function TestStage({
  data,
  accentColor,
  onAIOpen,
  onNextStage,
}: {
  data: TestQuestion[];
  chapterSlug: string;
  accentColor: string;
  onAIOpen: (position: string) => void;
  onNextStage: () => void;
}) {
  const questionResults = useLearnStore((s) => s.questionResults);
  const submitAnswer = useLearnStore((s) => s.submitAnswer);
  const testScore = useLearnStore((s) => s.testScore);
  const finishTest = useLearnStore((s) => s.finishTest);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const question = data[currentIdx];
  if (!question) return <p className="text-gray-500 text-center py-8">暂无测试题</p>;

  const result = questionResults[question.id];
  const hasSubmitted = !!result;
  const isChoice = question.q_type === 'choice';

  const handleSubmit = async () => {
    if (!userAnswer.trim() || submitting || hasSubmitted) return;
    setSubmitting(true);
    try {
      const feedback = await submitAnswer(question.id, userAnswer.trim(), question.difficulty, question.layer);
      if (feedback.is_correct) {
        toast.success('✅ 回答正确！');
      } else {
        toast.error('❌ 回答错误', {
          description: feedback.correct_answer ? `正确答案：${feedback.correct_answer}` : undefined,
        });
      }
    } catch (e) {
      toast.error('提交失败，请重试');
    }
    setSubmitting(false);
  };

  const handleChoiceSelect = (letter: string) => {
    setUserAnswer(letter);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSubmit();
  };

  const handleFinish = () => {
    finishTest();
    setShowResults(true);
  };

  const allAnswered = data.every((q) => !!questionResults[q.id]);

  // Show test results
  if (showResults && testScore) {
    const pct = Math.round((testScore.correct / testScore.total) * 100);
    const isGood = pct >= 80;

    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm text-center">
        <div className={`text-6xl mb-4 ${isGood ? '' : ''}`}>
          {isGood ? '🎉' : '📚'}
        </div>
        <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-2">
          测试完成！
        </h3>
        <div className={`text-5xl font-bold mb-2 ${isGood ? 'text-green-600' : 'text-orange-500'}`}>
          {pct}%
        </div>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          正确 {testScore.correct} / {testScore.total} 题
        </p>

        {/* Wrong questions */}
        {testScore.correct < testScore.total && (
          <div className="text-left mb-4">
            <h4 className="font-bold text-gray-700 dark:text-gray-300 mb-2">📝 错题回顾：</h4>
            <div className="space-y-2">
              {data.map((q) => {
                const r = questionResults[q.id];
                if (r?.isCorrect === false) {
                  return (
                    <div key={q.id} className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-sm">
                      <p
                        className="font-medium text-gray-800 dark:text-gray-200"
                        dangerouslySetInnerHTML={{ __html: renderMarkdown(q.stem) }}
                      />
                      <p className="text-red-600 dark:text-red-400 mt-1">
                        你的答案：{r.userAnswer}
                      </p>
                      {r.feedback && (
                        <>
                          <p
                            className="text-green-600 dark:text-green-400 mt-1"
                            dangerouslySetInnerHTML={{ __html: `正确答案：${renderMarkdown(r.feedback.correct_answer)}` }}
                          />
                          {r.feedback.explanation && (
                            <p
                              className="text-gray-600 dark:text-gray-400 mt-1 bg-white/50 dark:bg-gray-800/50 rounded p-2"
                              dangerouslySetInnerHTML={{ __html: `💡 ${renderMarkdown(r.feedback.explanation)}` }}
                            />
                          )}
                        </>
                      )}
                      <button
                        onClick={() => onAIOpen(`测试 错题 ${q.stem.slice(0, 20)}`)}
                        className="mt-2 text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400"
                      >
                        💬 问 AI 导师
                      </button>
                    </div>
                  );
                }
                return null;
              })}
            </div>
          </div>
        )}

        <div className="flex gap-3 justify-center">
          <button
            onClick={() => setShowResults(false)}
            className={`px-5 py-3 rounded-lg font-bold text-white ${accentColor}`}
          >
            查看题目详情
          </button>
          <button
            onClick={onNextStage}
            className="px-5 py-3 rounded-lg font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
          >
            进入总结 →
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm text-gray-500">
            第 {currentIdx + 1} 题 / 共 {data.length} 题
            <span className={`ml-2 px-2 py-0.5 rounded text-xs ${
              question.difficulty <= 2 ? 'bg-green-100 text-green-700' :
              question.difficulty === 3 ? 'bg-yellow-100 text-yellow-700' :
              'bg-red-100 text-red-700'
            }`}>
              难度 {question.difficulty}
            </span>
          </span>
          <button
            onClick={() => onAIOpen(`测试 第 ${currentIdx + 1} 题`)}
            className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
          >
            💬
          </button>
        </div>

        {/* Question */}
        <div className={`rounded-lg p-4 mb-4 text-lg text-center border-2 ${accentColor.replace('bg-', 'border-').replace('text-', 'border-')}/30 bg-gray-50 dark:bg-gray-900`}>
          <div dangerouslySetInnerHTML={{ __html: renderMarkdown(question.stem) }} />
        </div>

        {/* Answer input */}
        {!hasSubmitted ? (
          <div>
            {isChoice && question.options ? (
              <div className="space-y-3">
                <ChoiceInput
                  options={question.options}
                  isMath={accentColor === 'bg-blue-600'}
                  disabled={false}
                  onSelect={handleChoiceSelect}
                />
                <button
                  onClick={handleSubmit}
                  disabled={submitting || !userAnswer.trim()}
                  className={`w-full px-6 py-3 rounded-lg font-bold text-white transition-colors disabled:opacity-50 ${accentColor}`}
                >
                  {submitting ? '提交中...' : '提交答案'}
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <Input
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="输入你的答案..."
                  disabled={submitting}
                  className="flex-1 h-12 text-base"
                  autoFocus
                />
                <Button
                  onClick={handleSubmit}
                  disabled={submitting || !userAnswer.trim()}
                  className={accentColor}
                >
                  {submitting ? '提交中...' : '提交'}
                </Button>
              </div>
            )}
          </div>
        ) : (
          <div className={`rounded-lg p-4 border-2 ${
            result.isCorrect === true
              ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
              : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
          }`}>
            <p className={`font-bold text-lg mb-2 ${
              result.isCorrect === true ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'
            }`}>
              {result.isCorrect === true ? '✅ 正确！' : '❌ 错误'}
            </p>
            {result.feedback && (
              <>
                {/* Show explanation for ALL answers (correct and incorrect) */}
                {result.feedback.explanation && (
                  <p
                    className="text-sm text-gray-700 dark:text-gray-300 bg-white/50 dark:bg-gray-800/50 rounded p-3 mt-2"
                    dangerouslySetInnerHTML={{ __html: `💡 ${renderMarkdown(result.feedback.explanation)}` }}
                  />
                )}
                {/* For wrong answers, also show the correct answer */}
                {result.isCorrect === false && (
                  <p
                    className="text-sm text-green-600 dark:text-green-400 mt-2"
                    dangerouslySetInnerHTML={{ __html: `正确答案：${renderMarkdown(result.feedback.correct_answer)}` }}
                  />
                )}
                {result.feedback.hints && result.feedback.hints.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {result.feedback.hints.map((h, i) => (
                      <p key={i} className="text-xs text-gray-500" dangerouslySetInnerHTML={{ __html: `💭 ${renderMarkdown(h)}` }} />
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center mt-4">
        <button
          onClick={() => {
            setCurrentIdx(Math.max(0, currentIdx - 1));
            setUserAnswer('');
          }}
          disabled={currentIdx === 0}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            currentIdx === 0
              ? 'bg-gray-100 dark:bg-gray-800 text-gray-400 cursor-not-allowed'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300'
          }`}
        >
          ← 上一题
        </button>

        <div className="flex gap-2">
          {hasSubmitted && currentIdx < data.length - 1 && (
            <button
              onClick={() => {
                setCurrentIdx(currentIdx + 1);
                setUserAnswer('');
              }}
              className={`px-4 py-2 rounded-lg text-sm font-medium text-white ${accentColor}`}
            >
              下一题 →
            </button>
          )}
          {allAnswered && !showResults && (
            <button
              onClick={handleFinish}
              className="px-6 py-2 rounded-lg text-sm font-bold text-white bg-green-600 hover:bg-green-700 transition-colors"
            >
              📊 完成测试
            </button>
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div className="mt-4">
        <div className="flex justify-between text-xs text-muted-foreground mb-1">
          <span>答题进度</span>
          <span>{data.filter((q) => !!questionResults[q.id]).length} / {data.length}</span>
        </div>
        <Progress
          value={data.length > 0 ? (data.filter((q) => !!questionResults[q.id]).length / data.length) * 100 : 0}
          className="h-2"
        />
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════════
// 总结阶段
// ════════════════════════════════════════════════════════════

function SummaryStage({
  data,
  accentColor,
  onNextChapter,
  hasNextChapter,
  onAIOpen,
}: {
  data: SummaryData;
  accentColor: string;
  onNextChapter: () => void;
  hasNextChapter: boolean;
  onAIOpen: (position: string) => void;
}) {
  const testScore = useLearnStore((s) => s.testScore);

  return (
    <div className="space-y-6">
      {/* 完成卡片 */}
      <Card className={`overflow-hidden border-0 rounded-2xl bg-gradient-to-br ${accentColor.replace('bg-', 'from-').replace('text-', 'to-')} text-white text-center shadow-xl`}>
        <CardContent className="p-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-white/20 mb-4">
            <span className="text-4xl">🎉</span>
          </div>
          <h3 className="text-2xl font-bold mb-1">恭喜完成！</h3>
          <p className="text-white/70 text-sm mb-4">{data.chapter_title}</p>
          {testScore && (
            <div className="inline-flex flex-col items-center">
              <span className="text-5xl font-extrabold tracking-tight">
                {Math.round((testScore.correct / testScore.total) * 100)}%
              </span>
              <span className="text-white/60 text-xs mt-1">
                {testScore.correct}/{testScore.total} 正确
              </span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 关键知识点 */}
      {data.key_points && data.key_points.length > 0 && (
        <Card className="rounded-xl">
          <CardContent className="p-5">
            <h3 className="font-bold text-gray-800 dark:text-gray-200 mb-4">📌 本章关键点</h3>
            <ul className="space-y-3">
              {data.key_points.map((point, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-400">
                  <span className={`mt-0.5 w-6 h-6 rounded-full ${accentColor} text-white text-xs flex items-center justify-center shrink-0 font-bold`}>
                    {i + 1}
                  </span>
                  {point}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* 提示 */}
      {data.message && (
        <Card className="rounded-xl border-blue-200 dark:border-blue-800 bg-blue-50/50 dark:bg-blue-950/20">
          <CardContent className="p-4 text-sm text-blue-700 dark:text-blue-300">
            💡 {data.message}
          </CardContent>
        </Card>
      )}

      {/* 操作按钮 */}
      <div className="flex flex-wrap gap-3 justify-center">
        <Button
          variant="outline"
          onClick={() => onAIOpen('总结')}
        >
          💬 让 AI 帮我总结
        </Button>
        {hasNextChapter && (
          <Button
            onClick={onNextChapter}
            className={accentColor}
          >
            🚀 进入下一章 →
          </Button>
        )}
      </div>
    </div>
  );
}

// ════════════════════════════════════════════════════════════
// ════════════════════════════════════════════════════════════
// 主页面
// ════════════════════════════════════════════════════════════

export default function LearnPage() {
  const { subject } = useParams<{ subject: string }>();
  const navigate = useNavigate();

  const storeSubject = useLearnStore((s) => s.subject);
  const chapterSlug = useLearnStore((s) => s.chapterSlug);
  const chapterTitle = useLearnStore((s) => s.chapterTitle);
  const currentStage = useLearnStore((s) => s.currentStage);
  const stageData = useLearnStore((s) => s.stageData);
  const loading = useLearnStore((s) => s.loading);
  const error = useLearnStore((s) => s.error);
  const availableChapters = useLearnStore((s) => s.availableChapters);

  const setSubject = useLearnStore((s) => s.setSubject);
  const loadChapter = useLearnStore((s) => s.loadChapter);
  const goToStage = useLearnStore((s) => s.goToStage);
  const openAI = useLearnStore((s) => s.openAI);

  const accentColor = subject === 'math' ? 'bg-blue-600' : 'bg-emerald-600';
  const textColor = subject === 'math' ? 'text-blue-600' : 'text-emerald-600';
  const borderColor = subject === 'math' ? 'border-blue-600' : 'border-emerald-600';
  const label = subject === 'math' ? '🧮 数学' : '📖 英语';

  // Validate subject
  const validSubject = subject === 'math' || subject === 'english' ? subject : null;

  // Initialize subject
  useEffect(() => {
    if (validSubject && storeSubject !== validSubject) {
      setSubject(validSubject);
    }
  }, [validSubject, storeSubject, setSubject]);

  // Load first chapter when subject changes or no chapter loaded
  useEffect(() => {
    if (!validSubject) return;

    const loadFirstChapter = async () => {
      try {
        const { api } = await import('../api/client');
        const summary = await api.getProgressSummary(validSubject);
        const nodes = summary.nodes || [];

        // Find first non-mastered, non-locked chapter
        const firstAvailable = nodes.find(
          (n) => n.status === 'learning' || n.status === 'unlocked'
        );

        if (firstAvailable) {
          loadChapter(firstAvailable.slug);
        } else if (nodes.length > 0) {
          loadChapter(nodes[0].slug);
        }
      } catch (e) {
        console.error('Failed to load chapters:', e);
      }
    };

    loadFirstChapter();
  }, [validSubject]); // Reload when subject changes (don't depend on chapterSlug)

  // Restore stage data after refresh (persisted state has slug + stage but no data)
  useEffect(() => {
    if (chapterSlug && !stageData && !loading) {
      goToStage(currentStage);
    }
  }, [chapterSlug, currentStage, stageData, loading, goToStage]);

  if (!validSubject) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">请从首页选择学习科目</p>
      </div>
    );
  }

  if (loading && !chapterSlug) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className={`animate-spin rounded-full h-8 w-8 border-b-2 ${borderColor}`} />
          <p className="text-gray-500">加载学习内容...</p>
        </div>
      </div>
    );
  }

  if (error && !chapterSlug) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 mb-4">加载失败: {error}</p>
        <button
          onClick={() => window.location.reload()}
          className={`px-4 py-2 text-white rounded-lg ${accentColor}`}
        >
          重试
        </button>
      </div>
    );
  }

  // Find next chapter
  const currentChapterIdx = availableChapters.findIndex((n) => n.slug === chapterSlug);
  const nextChapter = currentChapterIdx >= 0 ? availableChapters[currentChapterIdx + 1] : null;

  const handleAIOpen = (position: string) => {
    openAI(position);
  };

  const handleNextChapter = () => {
    if (nextChapter) {
      loadChapter(nextChapter.slug);
    }
  };

  // Stage progression helper
  const stageOrder: Stage[] = ['concept', 'examples', 'practice', 'test', 'summary'];
  const goToNextStage = () => {
    const currentIdx = stageOrder.indexOf(currentStage);
    if (currentIdx >= 0 && currentIdx < stageOrder.length - 1) {
      goToStage(stageOrder[currentIdx + 1]);
    }
  };

  return (
    <div className="relative">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/')}
            className="mb-1"
          >
            ← 返回首页
          </Button>
          <h1 className={`text-xl font-bold ${textColor}`}>
            {label} · {chapterTitle || '加载中...'}
            <Badge variant={subject === 'math' ? 'secondary' : 'secondary'} className={`ml-2 text-xs ${subject === 'math' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'}`}>
              {subject === 'math' ? '📐 数学' : '🔤 英语'}
            </Badge>
          </h1>
        </div>
        <div className="flex items-center gap-2">
          {/* Chapter selector */}
          {availableChapters.length > 1 && (
            <select
              value={chapterSlug || ''}
              onChange={(e) => loadChapter(e.target.value)}
              className="text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 px-3 py-1.5 text-gray-700 dark:text-gray-300"
            >
              {availableChapters.map((ch) => (
                <option key={ch.slug} value={ch.slug}>
                  {ch.title} {ch.status === 'mastered' ? '✅' : ch.status === 'learning' ? '📖' : '🔒'}
                </option>
              ))}
            </select>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={() => openAI(currentStage === 'concept' ? '概念讲解' : '')}
            className={textColor}
            title="AI 导师"
          >
            💬 AI 导师
          </Button>
        </div>
      </div>

      {/* Stage Indicator */}
      <StageIndicator current={currentStage} onSelect={goToStage} isMath={subject === 'math'} />

      {/* Loading overlay */}
      {loading && (
        <div className="flex justify-center py-12">
          <div className={`animate-spin rounded-full h-6 w-6 border-b-2 ${borderColor}`} />
        </div>
      )}

      {/* Stage Content */}
      {!loading && stageData && (
        <div className="max-w-2xl mx-auto">
          {currentStage === 'concept' && (
            <ConceptStage data={stageData as ConceptData} accentColor={accentColor} onNextStage={goToNextStage} />
          )}

          {currentStage === 'examples' && (
            <ExampleStage
              data={stageData as ExampleData[]}
              accentColor={accentColor}
              onAIOpen={handleAIOpen}
              onNextStage={goToNextStage}
            />
          )}

          {currentStage === 'practice' && chapterSlug && (
            <PracticeStage
              data={stageData as PracticeQuestion[]}
              chapterSlug={chapterSlug}
              accentColor={accentColor}
              onAIOpen={handleAIOpen}
              onNextStage={goToNextStage}
            />
          )}

          {currentStage === 'test' && chapterSlug && (
            <TestStage
              data={stageData as TestQuestion[]}
              chapterSlug={chapterSlug}
              accentColor={accentColor}
              onAIOpen={handleAIOpen}
              onNextStage={goToNextStage}
            />
          )}

          {currentStage === 'summary' && (
            <SummaryStage
              data={stageData as SummaryData}
              accentColor={accentColor}
              onNextChapter={handleNextChapter}
              hasNextChapter={!!nextChapter}
              onAIOpen={handleAIOpen}
            />
          )}
        </div>
      )}

      {/* Error within stage */}
      {error && chapterSlug && (
        <div className="text-center py-8">
          <p className="text-red-500 mb-4">加载失败: {error}</p>
          <button
            onClick={() => goToStage(currentStage)}
            className={`px-4 py-2 text-white rounded-lg ${accentColor}`}
          >
            重试
          </button>
        </div>
      )}

      {/* AI Sidebar */}
      <AISidebar />
    </div>
  );
}
