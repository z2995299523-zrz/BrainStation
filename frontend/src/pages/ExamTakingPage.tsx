import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useExamStore } from '../stores/examStore';
import { renderMarkdown } from '../utils/renderMarkdown';

export default function ExamTakingPage() {
  const { examId } = useParams<{ examId: string }>();
  const navigate = useNavigate();
  const examIdNum = Number(examId);

  const {
    currentExam, currentAttempt, currentQuestionIndex,
    answers, result, loading, error,
    loadExam, startExam, submitAnswer, goToQuestion, finishExam,
  } = useExamStore();

  const [userInput, setUserInput] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // 加载考试和开始考试
  useEffect(() => {
    if (examIdNum) {
      loadExam(examIdNum).then(() => {
        startExam(examIdNum);
      });
    }
  }, [examIdNum]); // eslint-disable-line react-hooks/exhaustive-deps

  // 如果已有结果，跳转到结果页
  useEffect(() => {
    if (result) {
      navigate(`/exam/result/${examIdNum}`);
    }
  }, [result, examIdNum, navigate]);

  if (loading && !currentExam) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="animate-spin w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full mx-auto mb-3" />
        <p className="text-gray-400">加载考试...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <p className="text-red-500 mb-4">❌ {error}</p>
        <button
          onClick={() => navigate('/exam')}
          className="text-sm text-indigo-600 hover:text-indigo-700"
        >
          ← 返回考试列表
        </button>
      </div>
    );
  }

  if (!currentExam || !currentAttempt) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <p className="text-gray-400">考试不存在或尚未开始</p>
        <button
          onClick={() => navigate('/exam')}
          className="mt-4 text-sm text-indigo-600 hover:text-indigo-700"
        >
          ← 返回考试列表
        </button>
      </div>
    );
  }

  const questions = currentExam.questions || [];
  const currentQ = questions[currentQuestionIndex];
  const totalQuestions = questions.length;
  const answeredCount = Object.keys(answers).length;

  const handleSubmitAnswer = async () => {
    if (!currentQ || !userInput.trim() || submitting) return;
    setSubmitting(true);
    try {
      await submitAnswer(currentQ.id, userInput.trim());
      setUserInput('');
    } catch {
      // error handled by store
    } finally {
      setSubmitting(false);
    }
  };

  const handleFinish = async () => {
    if (answeredCount < totalQuestions) {
      if (!confirm(`还有 ${totalQuestions - answeredCount} 道题未作答，确定提交吗？\n\n未作答的题目将记为错误。`)) {
        return;
      }
    }
    await finishExam();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmitAnswer();
    }
  };

  const currentAnswer = currentQ ? answers[currentQ.id] : null;

  return (
    <div className="max-w-2xl mx-auto">
      {/* 头部 */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200">
            {currentExam.title}
          </h2>
          <p className="text-sm text-gray-500">
            第 {currentQuestionIndex + 1} / {totalQuestions} 题
            · 已答 {answeredCount} 题
          </p>
        </div>
        <button
          onClick={() => {
            if (confirm('确定退出考试吗？已作答的题目会保留。')) {
              navigate('/exam');
            }
          }}
          className="text-sm text-gray-400 hover:text-gray-600"
        >
          退出
        </button>
      </div>

      {/* 进度条 */}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-6">
        <div
          className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${(answeredCount / totalQuestions) * 100}%` }}
        />
      </div>

      {/* 题目 */}
      {currentQ && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 mb-4">
          {/* 难度标签 */}
          <div className="flex items-center gap-2 mb-3">
            <span className={`text-xs px-2 py-0.5 rounded-full ${
              currentQ.difficulty <= 2
                ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                : currentQ.difficulty <= 3
                ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
            }`}>
              难度: {'⭐'.repeat(currentQ.difficulty)}
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-500">
              {currentQ.q_type === 'choice' ? '选择题' : '填空题'}
            </span>
          </div>

          {/* 题干 */}
          <div
            className="text-gray-800 dark:text-gray-200 mb-6 text-lg leading-relaxed"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(currentQ.stem) }}
          />

          {/* 选择题 - 选项 */}
          {currentQ.q_type === 'choice' && currentQ.options && currentQ.options.length > 0 && (
            <div className="space-y-2 mb-6">
              {currentQ.options.map((opt) => {
                const letter = opt.trim().match(/^([A-D])/)?.[1] || opt[0];
                const cleaned = opt.replace(/^[A-D][:：.、]\s*/, '');
                const isSelected = userInput === letter;
                const isSubmitted = currentAnswer !== null;
                const isCorrectAnswer = isSubmitted && currentAnswer?.result?.correct_answer === letter;

                return (
                  <button
                    key={letter}
                    onClick={() => {
                      if (!currentAnswer) setUserInput(letter);
                    }}
                    disabled={!!currentAnswer}
                    className={`w-full text-left px-4 py-3 rounded-lg border text-sm transition-all ${
                      isSubmitted && isCorrectAnswer
                        ? 'border-green-400 bg-green-50 dark:bg-green-900/20 ring-1 ring-green-400'
                        : isSubmitted && isSelected && !currentAnswer?.result?.is_correct
                        ? 'border-red-400 bg-red-50 dark:bg-red-900/20 ring-1 ring-red-400'
                        : isSelected
                        ? 'border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20 ring-1 ring-indigo-400'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 bg-white dark:bg-gray-800'
                    } ${currentAnswer ? 'cursor-default' : 'cursor-pointer'}`}
                  >
                    <span className="font-bold text-gray-500 mr-2">{letter}.</span>
                    <span
                      className="text-gray-700 dark:text-gray-300"
                      dangerouslySetInnerHTML={{ __html: renderMarkdown(cleaned) }}
                    />
                    {isSubmitted && isCorrectAnswer && <span className="float-right text-green-600">✓</span>}
                    {isSubmitted && isSelected && !currentAnswer?.result?.is_correct && <span className="float-right text-red-500">✗</span>}
                  </button>
                );
              })}
            </div>
          )}

          {/* 填空题 - 输入框 */}
          {currentQ.q_type !== 'choice' && (
            <div className="mb-6">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="输入你的答案..."
                  disabled={!!currentAnswer}
                  className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
                />
              </div>
            </div>
          )}

          {/* 提交按钮 / 已答反馈 */}
          {!currentAnswer ? (
            <button
              onClick={handleSubmitAnswer}
              disabled={!userInput.trim() || submitting}
              className="w-full py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {submitting ? '提交中...' : '提交答案'}
            </button>
          ) : (
            <div className={`p-4 rounded-lg ${
              currentAnswer.result?.is_correct
                ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
            }`}>
              <p className={`font-medium mb-1 ${
                currentAnswer.result?.is_correct ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'
              }`}>
                {currentAnswer.result?.is_correct ? '✅ 回答正确' : '❌ 回答错误'}
              </p>
              {!currentAnswer.result?.is_correct && (
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  正确答案: <span className="font-medium">{currentAnswer.result?.correct_answer}</span>
                </p>
              )}
              {currentAnswer.result?.explanation && (
                <div
                  className="mt-2 text-sm text-gray-600 dark:text-gray-400 leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: renderMarkdown(currentAnswer.result.explanation) }}
                />
              )}
            </div>
          )}
        </div>
      )}

      {/* 底部导航 */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => goToQuestion(currentQuestionIndex - 1)}
            disabled={currentQuestionIndex === 0}
            className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            ← 上一题
          </button>
          <button
            onClick={() => goToQuestion(currentQuestionIndex + 1)}
            disabled={currentQuestionIndex >= totalQuestions - 1}
            className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            下一题 →
          </button>
        </div>

        {/* 快跳 */}
        <div className="flex gap-1 flex-wrap max-w-[200px]">
          {questions.map((_, i) => {
            const a = answers[questions[i].id];
            const isCurrent = i === currentQuestionIndex;
            return (
              <button
                key={i}
                onClick={() => goToQuestion(i)}
                className={`w-8 h-8 text-xs rounded-lg font-medium transition-colors ${
                  isCurrent
                    ? 'bg-indigo-600 text-white'
                    : a?.result?.is_correct
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                    : a
                    ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-500'
                }`}
              >
                {i + 1}
              </button>
            );
          })}
        </div>
      </div>

      {/* 完成按钮 */}
      <button
        onClick={handleFinish}
        disabled={loading}
        className="w-full mt-4 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
      >
        {loading ? '正在计算成绩...' : `完成考试 (${answeredCount}/${totalQuestions} 已答)`}
      </button>
    </div>
  );
}
