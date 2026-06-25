import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useExamStore } from '../stores/examStore';
import { useAuthStore } from '../stores/authStore';

export default function ExamListPage() {
  const navigate = useNavigate();
  const role = useAuthStore((s) => s.user?.role || 'learner');
  const { exams, loading, error, loadExams } = useExamStore();

  useEffect(() => {
    loadExams();
  }, [loadExams]);

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
          📋 综合考试
        </h2>
        {(role === 'examiner' || role === 'admin') && (
          <button
            onClick={() => navigate('/exam/manage')}
            className="text-sm px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            📝 考试管理
          </button>
        )}
      </div>

      {loading && (
        <div className="text-center py-12 text-gray-400">
          <div className="animate-spin w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full mx-auto mb-3" />
          加载中...
        </div>
      )}

      {error && (
        <div className="text-center py-12">
          <p className="text-red-500 mb-4">❌ {error}</p>
          <button
            onClick={() => loadExams()}
            className="text-sm text-indigo-600 hover:text-indigo-700"
          >
            点击重试
          </button>
        </div>
      )}

      {!loading && !error && exams.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <p className="text-5xl mb-4">📭</p>
          <p className="text-lg mb-2">暂无可参加的考试</p>
          <p className="text-sm">等待老师发布新的考试</p>
        </div>
      )}

      {!loading && exams.length > 0 && (
        <div className="space-y-4">
          {exams.map((exam) => (
            <div
              key={exam.id}
              className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-bold text-gray-800 dark:text-gray-200 text-lg">
                      {exam.title}
                    </h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      exam.subject === 'math'
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                        : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                    }`}>
                      {exam.subject === 'math' ? '📐 数学' : '🔤 英语'}
                    </span>
                  </div>
                  {exam.description && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                      {exam.description}
                    </p>
                  )}

                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500 dark:text-gray-400">
                    <span>📝 {exam.question_count} 题</span>
                    <span>⏱ {exam.time_limit_min} 分钟</span>
                    <span>📊 难度: {exam.difficulty_level}</span>
                    <span>✅ 及格线: {exam.passing_score}%</span>
                  </div>

                  {exam.last_score !== null && (
                    <div className="mt-3">
                      <span className={`text-sm font-medium ${
                        exam.last_score >= exam.passing_score
                          ? 'text-green-600'
                          : 'text-red-500'
                      }`}>
                        最近成绩: {exam.last_score}%
                        {exam.last_score >= exam.passing_score ? ' ✅' : ' ❌'}
                      </span>
                      {exam.attempts_count > 1 && (
                        <span className="text-xs text-gray-400 ml-2">
                          (共 {exam.attempts_count} 次)
                        </span>
                      )}
                    </div>
                  )}
                </div>

                <button
                  onClick={() => navigate(`/exam/take/${exam.id}`)}
                  className="shrink-0 ml-4 px-5 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  {exam.attempts_count > 0 ? '再次考试' : '开始考试'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
