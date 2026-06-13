import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { ProgressSummary } from '../types';

interface SubjectSummary {
  math: ProgressSummary | null;
  english: ProgressSummary | null;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [summaries, setSummaries] = useState<SubjectSummary>({ math: null, english: null });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getProgressSummary('math'),
      api.getProgressSummary('english'),
    ])
      .then(([math, english]) => setSummaries({ math, english }))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
          <p className="text-gray-500">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-center text-gray-800 dark:text-gray-200">
        🧠 初中数英思维训练营
      </h1>

      <div className="grid md:grid-cols-2 gap-6">
        {/* ── 数学卡片 ── */}
        <SubjectCard
          subject="math"
          label="数学"
          emoji="🧮"
          summary={summaries.math}
          onStart={() => navigate('/train/math')}
        />
        {/* ── 英语卡片 ── */}
        <SubjectCard
          subject="english"
          label="英语"
          emoji="📖"
          summary={summaries.english}
          onStart={() => navigate('/train/english')}
        />
      </div>
    </div>
  );
}

function SubjectCard({
  subject,
  label,
  emoji,
  summary,
  onStart,
}: {
  subject: 'math' | 'english';
  label: string;
  emoji: string;
  summary: ProgressSummary | null;
  onStart: () => void;
}) {
  const isMath = subject === 'math';
  const accentColor = isMath
    ? 'from-blue-500 to-indigo-600'
    : 'from-emerald-500 to-green-600';
  const bgColor = isMath
    ? 'border-blue-200 dark:border-blue-900 bg-blue-50/50 dark:bg-blue-950/30'
    : 'border-green-200 dark:border-green-900 bg-green-50/50 dark:bg-green-950/30';
  const btnColor = isMath
    ? 'bg-blue-600 hover:bg-blue-700'
    : 'bg-emerald-600 hover:bg-emerald-700';

  const mastered = summary?.mastered_nodes ?? 0;
  const total = summary?.total_nodes ?? 5;
  const pct = total > 0 ? Math.round((mastered / total) * 100) : 0;

  return (
    <div className={`rounded-2xl border ${bgColor} overflow-hidden`}>
      {/* Header */}
      <div className={`bg-gradient-to-r ${accentColor} px-6 py-4 text-white`}>
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold">{emoji} {label}</h2>
          <span className="text-sm opacity-80">
            {mastered}/{total} 已掌握
          </span>
        </div>
        {/* Progress bar */}
        <div className="mt-3 h-2 bg-white/30 rounded-full overflow-hidden">
          <div
            className="h-full bg-white rounded-full transition-all duration-700"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Node tree */}
      <div className="px-6 py-4 space-y-1">
        {summary?.nodes?.map((node) => {
          const icon =
            node.status === 'mastered' ? '✅' :
            node.status === 'learning' ? '📖' :
            node.status === 'unlocked' ? '🔓' : '🔒';
          return (
            <div key={node.slug} className="flex items-center gap-2 text-sm py-1">
              <span>{icon}</span>
              <span className={`flex-1 ${node.status === 'locked' ? 'text-gray-400' : 'text-gray-700 dark:text-gray-300'}`}>
                {node.title}
              </span>
              {node.status !== 'locked' && (
                <span className="text-xs text-gray-400">{Math.round(node.mastery_level * 100)}%</span>
              )}
            </div>
          );
        }) || <p className="text-sm text-gray-400 py-2">暂无数据，请先启动后端</p>}
      </div>

      {/* Stats + Action */}
      <div className="px-6 pb-5 space-y-3">
        <div className="flex gap-4 text-xs text-gray-500">
          <span>🎯 正确率 {summary ? Math.round((summary.overall_accuracy ?? 0) * 100) : 0}%</span>
          <span>📝 {summary?.total_attempts ?? 0} 题</span>
        </div>
        <button
          onClick={onStart}
          className={`w-full py-3 text-white font-bold rounded-xl transition-all active:scale-[0.98] shadow-md ${btnColor}`}
        >
          🚀 开始{label}训练
        </button>
      </div>
    </div>
  );
}
