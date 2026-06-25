import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useExamStore } from '../stores/examStore';
import { useLearnStore } from '../stores/learnStore';
import type { NodeProgress } from '../types';

export default function ExamManagePage() {
  const navigate = useNavigate();
  const {
    manageExams, loading,
    loadManageExams, generateExam, publishExam, deleteExam, loadManageResults,
    manageResults,
  } = useExamStore();
  const availableChapters = useLearnStore((s) => s.availableChapters);
  const loadAvailableChapters = useLearnStore((s) => s.loadAvailableChapters);

  // ── 创建表单状态 ──
  const [subject, setSubject] = useState<'math' | 'english'>('math');
  const [selectedChapters, setSelectedChapters] = useState<string[]>([]);
  const [questionCount, setQuestionCount] = useState(15);
  const [difficulty, setDifficulty] = useState('mixed');
  const [timeLimit, setTimeLimit] = useState(60);
  const [passingScore, setPassingScore] = useState(60);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState<string | null>(null);
  const [showResults, setShowResults] = useState<number | null>(null);

  useEffect(() => {
    loadManageExams();
  }, [loadManageExams]);

  useEffect(() => {
    if (availableChapters.length === 0) {
      loadAvailableChapters();
    }
  }, [availableChapters, loadAvailableChapters]);

  const filteredChapters = availableChapters.filter(
    (n: NodeProgress) => n.subject === subject
  );

  const toggleChapter = (slug: string) => {
    setSelectedChapters((prev) =>
      prev.includes(slug)
        ? prev.filter((s) => s !== slug)
        : [...prev, slug]
    );
  };

  const handleGenerate = async () => {
    if (selectedChapters.length === 0) {
      setGenError('请至少选择一个章节');
      return;
    }
    setGenerating(true);
    setGenError(null);
    try {
      const result = await generateExam({
        subject,
        chapter_slugs: selectedChapters,
        question_count: questionCount,
        difficulty_level: difficulty,
        title: title || undefined,
        description: description || undefined,
        time_limit_min: timeLimit,
        passing_score: passingScore,
      });
      if (result.error) {
        setGenError(result.error);
      } else {
        // Reset form
        setSelectedChapters([]);
        setTitle('');
        setDescription('');
        loadManageExams();
      }
    } catch (e) {
      setGenError((e as Error).message);
    } finally {
      setGenerating(false);
    }
  };

  const handleViewResults = async (examId: number) => {
    if (showResults === examId) {
      setShowResults(null);
      return;
    }
    setShowResults(examId);
    await loadManageResults(examId);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
          📝 考试管理
        </h2>
        <button
          onClick={() => navigate('/exam')}
          className="text-sm text-indigo-600 hover:text-indigo-700"
        >
          ← 返回考试列表
        </button>
      </div>

      {/* ── 创建考试 ── */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 mb-8">
        <h3 className="font-bold text-lg text-gray-800 dark:text-gray-200 mb-4">
          ✨ 创建新考试
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          {/* 学科选择 */}
          <div>
            <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              学科
            </label>
            <div className="flex gap-2">
              {(['math', 'english'] as const).map((s) => (
                <button
                  key={s}
                  onClick={() => { setSubject(s); setSelectedChapters([]); }}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    subject === s
                      ? s === 'math'
                        ? 'bg-blue-600 text-white'
                        : 'bg-emerald-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                  }`}
                >
                  {s === 'math' ? '📐 数学' : '🔤 英语'}
                </button>
              ))}
            </div>
          </div>

          {/* 难度 */}
          <div>
            <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              难度级别
            </label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-sm"
            >
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="mixed">混合</option>
              <option value="hard">困难</option>
            </select>
          </div>

          {/* 题数 */}
          <div>
            <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              题目数量: {questionCount}
            </label>
            <input
              type="range"
              min={5}
              max={50}
              value={questionCount}
              onChange={(e) => setQuestionCount(Number(e.target.value))}
              className="w-full"
            />
          </div>

          {/* 时间限制 */}
          <div>
            <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              时间限制: {timeLimit} 分钟
            </label>
            <input
              type="range"
              min={10}
              max={180}
              step={10}
              value={timeLimit}
              onChange={(e) => setTimeLimit(Number(e.target.value))}
              className="w-full"
            />
          </div>

          {/* 及格线 */}
          <div>
            <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              及格线: {passingScore}%
            </label>
            <input
              type="range"
              min={10}
              max={100}
              step={5}
              value={passingScore}
              onChange={(e) => setPassingScore(Number(e.target.value))}
              className="w-full"
            />
          </div>

          {/* 标题 */}
          <div>
            <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              考试标题 (可选)
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="自动生成..."
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-sm"
            />
          </div>
        </div>

        {/* 描述 */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
            考试描述 (可选)
          </label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="简要说明考试范围..."
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-sm"
          />
        </div>

        {/* 章节选择 */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
            选择章节 ({selectedChapters.length} 已选)
          </label>
          <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto">
            {filteredChapters.length === 0 && (
              <p className="text-sm text-gray-400">请先进入学科学习页面加载章节列表</p>
            )}
            {filteredChapters.map((ch: NodeProgress) => (
              <button
                key={ch.slug}
                onClick={() => toggleChapter(ch.slug)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  selectedChapters.includes(ch.slug)
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {ch.title}
              </button>
            ))}
          </div>
        </div>

        {genError && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm rounded-lg">
            ❌ {genError}
          </div>
        )}

        <button
          onClick={handleGenerate}
          disabled={generating || selectedChapters.length === 0}
          className="w-full py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {generating ? (
            <span className="flex items-center justify-center gap-2">
              <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
              AI 正在出题...
            </span>
          ) : (
            '🤖 AI 生成考试'
          )}
        </button>
      </div>

      {/* ── 考试列表 ── */}
      <div>
        <h3 className="font-bold text-lg text-gray-800 dark:text-gray-200 mb-4">
          📚 已创建的考试
        </h3>

        {loading && (
          <div className="text-center py-8 text-gray-400">
            <div className="animate-spin w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full mx-auto mb-2" />
            加载中...
          </div>
        )}

        {!loading && manageExams.length === 0 && (
          <div className="text-center py-8 text-gray-400">
            <p className="text-3xl mb-2">📭</p>
            <p>还没有创建任何考试</p>
          </div>
        )}

        {manageExams.map((exam) => (
          <div
            key={exam.id}
            className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-3"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-medium text-gray-800 dark:text-gray-200">
                    {exam.title}
                  </h4>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    exam.status === 'published'
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                      : exam.status === 'draft'
                      ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                  }`}>
                    {exam.status === 'published' ? '已发布' : exam.status === 'draft' ? '草稿' : '已归档'}
                  </span>
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 space-x-3">
                  <span>{exam.subject === 'math' ? '📐 数学' : '🔤 英语'}</span>
                  <span>{exam.question_count} 题</span>
                  <span>{exam.time_limit_min} 分钟</span>
                  <span>{exam.attempt_count} 人参加</span>
                </div>
              </div>

              <div className="flex items-center gap-2 ml-4 shrink-0">
                <button
                  onClick={() => handleViewResults(exam.id)}
                  className="text-xs px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  📊 成绩
                </button>
                {exam.status !== 'published' && (
                  <button
                    onClick={() => publishExam(exam.id)}
                    className="text-xs px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    发布
                  </button>
                )}
                <button
                  onClick={() => {
                    if (confirm('确定删除这个考试吗？所有考试记录将被删除。')) {
                      deleteExam(exam.id);
                    }
                  }}
                  className="text-xs px-3 py-1.5 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors"
                >
                  删除
                </button>
              </div>
            </div>

            {/* 成绩展开 */}
            {showResults === exam.id && manageResults && manageResults.exam_id === exam.id && (
              <div className="mt-4 border-t border-gray-100 dark:border-gray-700 pt-4">
                <div className="flex gap-4 mb-3 text-sm">
                  <span className="text-gray-500">参加人数: <strong>{manageResults.total_attempts}</strong></span>
                  <span className="text-gray-500">平均分: <strong>{manageResults.avg_score.toFixed(1)}%</strong></span>
                  <span className="text-gray-500">及格线: <strong>{manageResults.passing_score}%</strong></span>
                </div>
                {manageResults.results.length === 0 ? (
                  <p className="text-sm text-gray-400">还没有人参加考试</p>
                ) : (
                  <div className="space-y-2">
                    {manageResults.results.map((r) => (
                      <div key={r.attempt_id} className="flex items-center justify-between text-sm bg-gray-50 dark:bg-gray-750 rounded px-3 py-2">
                        <span className="text-gray-700 dark:text-gray-300">👤 {r.username}</span>
                        <span className={`font-medium ${r.passed ? 'text-green-600' : 'text-red-500'}`}>
                          {r.score}% {r.passed ? '✅' : '❌'}
                        </span>
                        <span className="text-xs text-gray-400">{r.correct_count}/{r.total_questions}</span>
                        <span className="text-xs text-gray-400">{r.completed_at?.slice(0, 16)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
