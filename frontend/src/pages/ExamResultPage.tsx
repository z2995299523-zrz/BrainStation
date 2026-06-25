import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useExamStore } from '../stores/examStore';
import { renderMarkdown } from '../utils/renderMarkdown';

export default function ExamResultPage() {
  const { examId } = useParams<{ examId: string }>();
  const navigate = useNavigate();
  const examIdNum = Number(examId);

  const { result, loading, error, loadExam, startExam, resetExam } = useExamStore();

  useEffect(() => {
    // result should already be loaded from finishExam in ExamTakingPage
    // If not (e.g. directly navigated), redirect
    if (!result && !loading) {
      // Try to get result from params
      const searchParams = new URLSearchParams(window.location.search);
      const attemptId = searchParams.get('attempt');
      if (attemptId && examIdNum) {
        // Result will be loaded by parent
      }
    }
  }, [result, loading, examIdNum]);

  const handleRetake = async () => {
    if (!examIdNum) return;
    resetExam();
    await loadExam(examIdNum);
    await startExam(examIdNum);
    navigate(`/exam/take/${examIdNum}`);
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="animate-spin w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full mx-auto mb-3" />
        <p className="text-gray-400">加载成绩...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <p className="text-red-500 mb-4">❌ {error}</p>
        <button onClick={() => navigate('/exam')} className="text-indigo-600">
          ← 返回考试列表
        </button>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <p className="text-gray-400 mb-4">暂无考试结果</p>
        <button onClick={() => navigate('/exam')} className="text-indigo-600">
          ← 返回考试列表
        </button>
      </div>
    );
  }

  const passed = result.passed;

  return (
    <div className="max-w-3xl mx-auto">
      {/* 成绩卡片 */}
      <div className={`rounded-2xl p-8 mb-8 text-white text-center ${
        passed
          ? 'bg-gradient-to-br from-green-500 to-emerald-600'
          : 'bg-gradient-to-br from-red-500 to-rose-600'
      }`}>
        <p className="text-5xl mb-2">{passed ? '🎉' : '😞'}</p>
        <h2 className="text-2xl font-bold mb-1">
          {passed ? '恭喜通过!' : '未通过'}
        </h2>
        <p className="text-white/80 text-sm mb-6">{result.exam_title}</p>

        <div className="text-6xl font-extrabold mb-2">
          {result.score ?? 0}<span className="text-2xl">%</span>
        </div>
        <p className="text-white/80">
          正确 {result.correct_count}/{result.total_questions} 题
          · 及格线 {result.passing_score}%
        </p>

        <div className="mt-6 w-full bg-white/20 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-1000 ${
              passed ? 'bg-white' : 'bg-yellow-300'
            }`}
            style={{ width: `${result.score ?? 0}%` }}
          />
        </div>
      </div>

      {/* 薄弱章节 */}
      {result.weak_areas && result.weak_areas.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 mb-6">
          <h3 className="font-bold text-lg text-gray-800 dark:text-gray-200 mb-4">
            ⚠️ 需要加强的章节
          </h3>
          <div className="space-y-3">
            {result.weak_areas.map((area) => (
              <div key={area.chapter_slug}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-700 dark:text-gray-300">
                    {area.chapter_title}
                  </span>
                  <span className={`font-medium ${
                    area.accuracy >= 0.6 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {area.error_count}/{area.total_count} 错 · {Math.round(area.accuracy * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      area.accuracy >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${area.accuracy * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 错题回顾 */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <h3 className="font-bold text-lg text-gray-800 dark:text-gray-200 mb-4">
          📝 答题详览
        </h3>
        <div className="space-y-4">
          {result.answers.map((a, i) => (
            <div
              key={a.question_id}
              className={`p-4 rounded-lg border ${
                a.is_correct
                  ? 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/10'
                  : 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/10'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <span className="text-sm font-medium text-gray-500">
                  第 {i + 1} 题
                  {a.chapter_slug && (
                    <span className="ml-2 text-xs text-gray-400">({a.chapter_slug})</span>
                  )}
                </span>
                <span className={a.is_correct ? 'text-green-600' : 'text-red-600'}>
                  {a.is_correct ? '✅ 正确' : '❌ 错误'}
                </span>
              </div>

              <div
                className="text-gray-800 dark:text-gray-200 mb-3"
                dangerouslySetInnerHTML={{ __html: renderMarkdown(a.stem) }}
              />

              {!a.is_correct && (
                <div className="text-sm space-y-1">
                  <p className="text-gray-600 dark:text-gray-400">
                    你的答案: <span className="text-red-600 font-medium">{a.user_answer}</span>
                  </p>
                  <p className="text-gray-600 dark:text-gray-400">
                    正确答案: <span className="text-green-600 font-medium">{a.correct_answer}</span>
                  </p>
                </div>
              )}

              {a.explanation && (
                <div
                  className="mt-3 text-sm text-gray-600 dark:text-gray-400 leading-relaxed border-t border-gray-200 dark:border-gray-700 pt-3"
                  dangerouslySetInnerHTML={{ __html: `💡 ${renderMarkdown(a.explanation)}` }}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="flex gap-3">
        <button
          onClick={handleRetake}
          className="flex-1 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          🔄 再次考试
        </button>
        <button
          onClick={() => navigate('/exam')}
          className="flex-1 py-3 border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 font-medium rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          ← 返回列表
        </button>
      </div>
    </div>
  );
}
