import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { api } from '../api/client';
import type { ProgressSummary } from '../types';
import KnowledgeTree from '../components/shared/KnowledgeTree';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';

interface SubjectSummary {
  math: ProgressSummary | null;
  english: ProgressSummary | null;
}

// ── 圆形进度环 ──
function CircleProgress({ pct, size = 72, strokeWidth = 6, color }: {
  pct: number;
  size?: number;
  strokeWidth?: number;
  color: string;
}) {
  const r = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * r;
  const offset = circumference - (pct / 100) * circumference;
  return (
    <svg width={size} height={size} className="shrink-0">
      <circle cx={size / 2} cy={size / 2} r={r}
        fill="none" stroke="currentColor"
        className="text-gray-200 dark:text-gray-700"
        strokeWidth={strokeWidth} />
      <circle cx={size / 2} cy={size / 2} r={r}
        fill="none" stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        className="transition-all duration-1000 ease-out"
        transform={`rotate(-90 ${size / 2} ${size / 2})`} />
      <text x="50%" y="50%" dominantBaseline="central" textAnchor="middle"
        className="fill-gray-800 dark:fill-gray-200 font-bold"
        style={{ fontSize: size * 0.24 }}>
        {pct}%
      </text>
    </svg>
  );
}

// ── 统计卡片 ──
function StatCard({ icon, label, value, color }: {
  icon: string; label: string; value: string | number; color: string;
}) {
  return (
    <div className="flex items-center gap-3 bg-white dark:bg-gray-800/50 rounded-xl px-4 py-3 border border-gray-100 dark:border-gray-700/50">
      <span className="text-2xl">{icon}</span>
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className={`text-lg font-bold ${color}`}>{value}</p>
      </div>
    </div>
  );
}

// ── 学科大卡片 ──
function SubjectCard({
  subject, label, emoji, summary, onStart,
}: {
  subject: 'math' | 'english';
  label: string;
  emoji: string;
  summary: ProgressSummary | null;
  onStart: () => void;
}) {
  const isMath = subject === 'math';
  const mastered = summary?.mastered_nodes ?? 0;
  const total = summary?.total_nodes ?? 5;
  const pct = total > 0 ? Math.round((mastered / total) * 100) : 0;
  const accuracy = Math.round((summary?.overall_accuracy ?? 0) * 100);
  const attempts = summary?.total_attempts ?? 0;

  const bgGradient = isMath
    ? 'from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20'
    : 'from-emerald-50 to-green-50 dark:from-emerald-950/20 dark:to-green-950/20';
  const iconBg = isMath
    ? 'bg-blue-100 dark:bg-blue-900/40'
    : 'bg-emerald-100 dark:bg-emerald-900/40';
  const ringColor = isMath ? '#3b82f6' : '#10b981';
  const buttonGradient = isMath
    ? 'from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500'
    : 'from-emerald-600 to-green-600 hover:from-emerald-500 hover:to-green-500';
  const borderHover = isMath
    ? 'hover:border-blue-300 dark:hover:border-blue-700'
    : 'hover:border-emerald-300 dark:hover:border-emerald-700';

  return (
    <Card className={`group overflow-hidden rounded-2xl border border-gray-100 dark:border-gray-700/50 shadow-sm hover:shadow-xl transition-all duration-300 ${borderHover}`}>
      <div className={`bg-gradient-to-br ${bgGradient} p-6`}>
        {/* Header row */}
        <div className="flex items-start justify-between mb-5">
          <div className="flex items-center gap-3">
            <span className={`w-12 h-12 ${iconBg} rounded-2xl flex items-center justify-center text-2xl`}>
              {emoji}
            </span>
            <div>
              <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200">{label}</h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                {mastered}/{total} 章节已掌握
              </p>
            </div>
          </div>
          <CircleProgress pct={pct} color={ringColor} />
        </div>

        {/* Mini stats */}
        <div className="flex gap-4 mb-5">
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <span>🎯</span>
            <span className="font-semibold text-gray-700 dark:text-gray-300">{accuracy}%</span>
            <span className="text-xs">正确率</span>
          </div>
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <span>📝</span>
            <span className="font-semibold text-gray-700 dark:text-gray-300">{attempts}</span>
            <span className="text-xs">题</span>
          </div>
        </div>

        {/* CTA */}
        <Button
          onClick={onStart}
          size="lg"
          className={`w-full bg-gradient-to-r ${buttonGradient} text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-200 active:scale-[0.98] h-12 text-base`}
        >
          🚀 开始{label}学习
        </Button>
      </div>

      {/* Knowledge tree */}
      <CardContent className="p-5">
        <p className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wider">
          📊 知识结构
        </p>
        {summary?.nodes && summary.nodes.length > 0 ? (
          <KnowledgeTree nodes={summary.nodes} subject={subject} />
        ) : (
          <p className="text-sm text-muted-foreground py-2">
            加载中...
          </p>
        )}
      </CardContent>
    </Card>
  );
}

// ── 加载骨架屏 ──
function DashboardSkeleton() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="text-center space-y-2">
        <Skeleton className="h-8 w-48 mx-auto" />
        <Skeleton className="h-4 w-32 mx-auto" />
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[1, 2, 3, 4].map(i => (
          <Skeleton key={i} className="h-16 rounded-xl" />
        ))}
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        <Skeleton className="h-80 rounded-2xl" />
        <Skeleton className="h-80 rounded-2xl" />
      </div>
    </div>
  );
}

// ════════════════════════════════════════
// 主页面
// ════════════════════════════════════════

export default function Dashboard() {
  const navigate = useNavigate();
  const user = useAuthStore(s => s.user);
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

  if (loading) return <DashboardSkeleton />;

  const mathTotal = (summaries.math?.total_nodes ?? 0);
  const engTotal = (summaries.english?.total_nodes ?? 0);
  const mathMastered = (summaries.math?.mastered_nodes ?? 0);
  const engMastered = (summaries.english?.mastered_nodes ?? 0);
  const totalMastered = mathMastered + engMastered;
  const totalNodes = mathTotal + engTotal;
  const totalAttempts = (summaries.math?.total_attempts ?? 0) + (summaries.english?.total_attempts ?? 0);
  const avgAccuracy = totalAttempts > 0
    ? Math.round(
        ((summaries.math?.overall_accuracy ?? 0) * (summaries.math?.total_attempts ?? 0) +
         (summaries.english?.overall_accuracy ?? 0) * (summaries.english?.total_attempts ?? 0)) /
        totalAttempts * 100)
    : 0;
  const streak = summaries.math?.streak_days ?? 0;

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* ── Welcome section ── */}
      <div className="text-center space-y-2 pt-4">
        <h1 className="text-3xl font-extrabold text-gray-900 dark:text-gray-100 tracking-tight">
          {user ? `👋 欢迎回来，${user.username}` : '🧠 初中数英思维训练营'}
        </h1>
        <p className="text-muted-foreground text-sm">
          {streak > 0
            ? `已连续学习 ${streak} 天，继续保持！`
            : '新的一天，开始学习吧 ✨'}
        </p>
      </div>

      {/* ── Stats row ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard icon="📚" label="已掌握章节" value={`${totalMastered}/${totalNodes}`} color="text-indigo-600 dark:text-indigo-400" />
        <StatCard icon="🎯" label="综合正确率" value={`${avgAccuracy}%`} color="text-green-600 dark:text-green-400" />
        <StatCard icon="📝" label="累计练习" value={`${totalAttempts} 题`} color="text-blue-600 dark:text-blue-400" />
        <StatCard icon="🔥" label="连续学习" value={`${streak} 天`} color="text-orange-500" />
      </div>

      {/* ── Subject cards ── */}
      <div className="grid md:grid-cols-2 gap-6">
        <SubjectCard
          subject="math" label="数学" emoji="🧮"
          summary={summaries.math}
          onStart={() => navigate('/learn/math')}
        />
        <SubjectCard
          subject="english" label="英语" emoji="📖"
          summary={summaries.english}
          onStart={() => navigate('/learn/english')}
        />
      </div>
    </div>
  );
}
