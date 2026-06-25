import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Tooltip, TooltipTrigger, TooltipContent } from '../components/ui/tooltip';
import type { UserManageItem } from '../types';

// 帮助图标 + 提示
function HelpIcon({ text }: { text: string }) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span className="inline-flex items-center justify-center w-4 h-4 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 text-[10px] cursor-help leading-none ml-1.5 select-none">?</span>
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-[320px] leading-relaxed">
        {text}
      </TooltipContent>
    </Tooltip>
  );
}

interface Sm2Node {
  slug: string;
  title: string;
  subject: string;
  tier: string;
  mastery: number;
  ef: number;
  interval: number;
  repetitions: number;
  next_review_at: string | null;
  status: string;
}

export default function AdminPage() {
  const [nodes, setNodes] = useState<Sm2Node[]>([]);
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState<UserManageItem[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [selectedUsername, setSelectedUsername] = useState('');
  const [overrideSlug, setOverrideSlug] = useState('');
  const [overrideEF, setOverrideEF] = useState('2.5');
  const [overrideMastery, setOverrideMastery] = useState('0');
  const [overrideStatus, setOverrideStatus] = useState('learning');
  const [configParam, setConfigParam] = useState('sm2.initial_ef');
  const [configValue, setConfigValue] = useState('2.5');
  const [msg, setMsg] = useState('');

  // Load users for selector
  useEffect(() => {
    api.getUsers().then((data) => {
      const list = (data.users as unknown as UserManageItem[]) ?? [];
      setUsers(list);
    }).catch(() => {});
  }, []);

  const fetchNodes = (userId?: number) => {
    setLoading(true);
    api.getSm2State(userId).then((data) => {
      setNodes(data.nodes as unknown as Sm2Node[]);
      if (data.target_user) {
        setSelectedUsername((data.target_user).username as string || '');
        setSelectedUserId((data.target_user).id as number || null);
      }
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => { fetchNodes(); }, []);

  const handleUserChange = (userId: string) => {
    if (!userId) {
      fetchNodes();
      return;
    }
    fetchNodes(Number(userId));
  };

  const handleOverride = async () => {
    await api.overrideSm2({
      node_slug: overrideSlug,
      user_id: selectedUserId,
      ef: parseFloat(overrideEF),
      mastery_level: parseFloat(overrideMastery),
      status: overrideStatus,
    });
    setMsg(`已覆盖: ${overrideSlug}${selectedUsername ? ` (用户: ${selectedUsername})` : ''}`);
    // Refresh current view
    if (selectedUserId) {
      handleUserChange(String(selectedUserId));
    } else {
      fetchNodes();
    }
  };

  const handleConfigUpdate = async () => {
    await api.updateConfig({ param_path: configParam, new_value: configValue });
    setMsg(`配置已更新: ${configParam} = ${configValue}`);
  };

  const handleReload = async () => {
    const result = await api.reloadContent();
    setMsg(`内容已重载: ${result.nodes_loaded} 节点, ${result.questions_loaded} 题`);
    fetchNodes();
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
          ⚙️ 管理面板
        </h1>
      </div>

      {msg && (
        <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-sm text-green-700 dark:text-green-400">
          ✅ {msg}
          <button onClick={() => setMsg('')} className="ml-2 text-green-500 hover:text-green-700">✕</button>
        </div>
      )}

      {/* ── User selector ── */}
      <Card>
        <CardContent className="p-4 flex items-center gap-4">
          <span className="text-sm font-medium text-gray-600 dark:text-gray-400 whitespace-nowrap">
            👤 查看用户
            <HelpIcon text="选择要查看或管理哪个用户的学习状态。默认显示你自己的 SM-2 数据。切换用户后，下方的调试表和覆盖操作都作用于该用户。" />
          </span>
          <select
            value={selectedUserId ?? ''}
            onChange={(e) => handleUserChange(e.target.value)}
            className="flex-1 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 px-3 py-2 text-gray-700 dark:text-gray-300 max-w-xs"
          >
            <option value="">我自己 (管理员)</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.username} ({u.role === 'admin' ? '管理员' : u.role === 'examiner' ? '考核者' : '学习者'})
              </option>
            ))}
          </select>
          {selectedUsername && (
            <span className="text-xs text-muted-foreground">
              当前查看: <strong>{selectedUsername}</strong> 的 SM-2 状态
            </span>
          )}
        </CardContent>
      </Card>

      {/* ── SM-2 Debug Table ── */}
      <Card>
        <CardContent className="p-4">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3">
            📊 SM-2 调试器
            <HelpIcon text={`SM-2 (SuperMemo 2) 间隔重复算法状态表。

各列含义：
• 掌握度 — 0~1 综合评分，≥0.85可解锁后续章节
• EF (Easiness Factor) — 难度系数，默认2.5，越高越容易记住。答对上升，答错下降，最低1.3
• 间隔 — 当前设定多少天后复习
• 状态 — locked(未解锁)→unlocked→learning→mastered(已掌握)→degraded(退化)
• 下次复习 — 到该日期建议复习，逾期未复习掌握度会衰减`} />
          </h2>
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin h-6 w-6 border-b-2 border-indigo-600 rounded-full" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700 text-left">
                    <th className="p-2 text-gray-500 dark:text-gray-400 font-medium">节点</th>
                    <th className="p-2 text-gray-500 dark:text-gray-400 font-medium">学科</th>
                    <th className="p-2 text-gray-500 dark:text-gray-400 font-medium">掌握度</th>
                    <th className="p-2 text-gray-500 dark:text-gray-400 font-medium">EF</th>
                    <th className="p-2 text-gray-500 dark:text-gray-400 font-medium">间隔</th>
                    <th className="p-2 text-gray-500 dark:text-gray-400 font-medium">状态</th>
                    <th className="p-2 text-gray-500 dark:text-gray-400 font-medium">下次复习</th>
                  </tr>
                </thead>
                <tbody>
                  {nodes.map((n) => (
                    <tr key={n.slug} className="border-b border-gray-100 dark:border-gray-700/50">
                      <td className="p-2 font-medium text-gray-800 dark:text-gray-200">{n.title}</td>
                      <td className="p-2">{n.subject === 'math' ? '🧮' : '📖'}</td>
                      <td className="p-2">{(n.mastery * 100).toFixed(0)}%</td>
                      <td className="p-2">{n.ef?.toFixed(2)}</td>
                      <td className="p-2">{n.interval}天</td>
                      <td className="p-2">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                          n.status === 'mastered' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                          n.status === 'learning' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' :
                          n.status === 'locked' ? 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400' :
                          'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                        }`}>{n.status}</span>
                      </td>
                      <td className="p-2 text-xs text-muted-foreground">{n.next_review_at || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ── Override Form ── */}
      <Card>
        <CardContent className="p-5 space-y-3">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            🔧 手动覆盖
            <HelpIcon text={`手动修改某个章节的 SM-2 参数。

使用场景：
• 学生卡住无法解锁 → 设为 unlocked
• 误标记为 mastered → 降回 learning 重新学习
• 测试算法行为 → 调整 EF 观察间隔变化
• 加快进度 → 提高掌握度至 0.9+ 直接跳过

slug 从上方调试表中复制，如 "factorization"。修改记录会写入变更日志。`} />
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div>
              <label className="block text-xs text-gray-500 mb-1">节点 slug</label>
              <Input value={overrideSlug} onChange={(e) => setOverrideSlug(e.target.value)}
                placeholder="如: factorization" className="text-sm" />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">EF (≥1.3)</label>
              <Input value={overrideEF} onChange={(e) => setOverrideEF(e.target.value)}
                className="text-sm" />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">掌握度 (0~1)</label>
              <Input value={overrideMastery} onChange={(e) => setOverrideMastery(e.target.value)}
                className="text-sm" />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">状态</label>
              <select value={overrideStatus} onChange={(e) => setOverrideStatus(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg text-sm bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300">
                <option value="locked">locked</option>
                <option value="unlocked">unlocked</option>
                <option value="learning">learning</option>
                <option value="mastered">mastered</option>
                <option value="degraded">degraded</option>
              </select>
            </div>
          </div>
          <Button onClick={handleOverride} className="bg-indigo-600 hover:bg-indigo-700">
            执行覆盖 {selectedUsername ? `→ ${selectedUsername}` : ''}
          </Button>
        </CardContent>
      </Card>

      {/* ── Config + Reload ── */}
      <Card>
        <CardContent className="p-5 space-y-3">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            ⚡ 参数调节
            <HelpIcon text={`运行时修改 config.yaml 配置参数，自动热加载无需重启。

参数路径用 "." 分隔，常用参数：
• sm2.initial_ef — 新章节初始 EF 值（默认2.5）
• sm2.mastery_threshold — 何时算掌握（默认0.85）
• sm2.min_ef — 最低 EF（默认1.3）

修改会写入 config_changelog 表，有审计记录。
重新加载内容：重新读取 content/ 下所有 YAML 教学文件。`} />
          </h2>
          <div className="flex gap-3 items-end flex-wrap">
            <div>
              <label className="block text-xs text-gray-500 mb-1">参数路径</label>
              <Input value={configParam} onChange={(e) => setConfigParam(e.target.value)}
                className="text-sm w-48" />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">新值</label>
              <Input value={configValue} onChange={(e) => setConfigValue(e.target.value)}
                className="text-sm w-32" />
            </div>
            <Button onClick={handleConfigUpdate} variant="secondary">
              保存
            </Button>
          </div>

          <div className="border-t pt-3 mt-3">
            <Button onClick={handleReload} variant="outline">
              重新加载内容
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
