import { useEffect, useState } from 'react';
import { api } from '../api/client';

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
  const [overrideSlug, setOverrideSlug] = useState('');
  const [overrideEF, setOverrideEF] = useState('2.5');
  const [overrideMastery, setOverrideMastery] = useState('0');
  const [overrideStatus, setOverrideStatus] = useState('learning');
  const [configParam, setConfigParam] = useState('sm2.initial_ef');
  const [configValue, setConfigValue] = useState('2.5');
  const [msg, setMsg] = useState('');

  const fetchNodes = () => {
    api.getSm2State().then((data) => {
      setNodes(data.nodes as unknown as Sm2Node[]);
      setLoading(false);
    });
  };

  useEffect(() => { fetchNodes(); }, []);

  const handleOverride = async () => {
    await api.overrideSm2({
      node_slug: overrideSlug,
      ef: parseFloat(overrideEF),
      mastery_level: parseFloat(overrideMastery),
      status: overrideStatus,
    });
    setMsg(`已覆盖: ${overrideSlug}`);
    fetchNodes();
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

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin h-8 w-8 border-b-2 border-indigo-600 rounded-full" />
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold">⚙️ 管理面板</h1>

      {msg && (
        <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 rounded-lg text-sm text-green-700">
          {msg}
        </div>
      )}

      {/* 1. SM-2 Debug Table */}
      <section>
        <h2 className="text-lg font-semibold mb-3">📊 SM-2 调试器</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-800 text-left">
                <th className="p-2">节点</th>
                <th className="p-2">学科</th>
                <th className="p-2">掌握度</th>
                <th className="p-2">EF</th>
                <th className="p-2">间隔</th>
                <th className="p-2">状态</th>
                <th className="p-2">下次复习</th>
              </tr>
            </thead>
            <tbody>
              {nodes.map((n) => (
                <tr key={n.slug} className="border-b border-gray-100 dark:border-gray-800">
                  <td className="p-2 font-medium">{n.title}</td>
                  <td className="p-2">{n.subject === 'math' ? '🧮' : '📖'}</td>
                  <td className="p-2">{(n.mastery * 100).toFixed(0)}%</td>
                  <td className="p-2">{n.ef?.toFixed(2)}</td>
                  <td className="p-2">{n.interval}天</td>
                  <td className="p-2">
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      n.status === 'mastered' ? 'bg-green-100 text-green-700' :
                      n.status === 'learning' ? 'bg-blue-100 text-blue-700' :
                      n.status === 'locked' ? 'bg-gray-100 text-gray-500' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>{n.status}</span>
                  </td>
                  <td className="p-2 text-xs text-gray-400">{n.next_review_at || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* 2. Override Form */}
      <section className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800 space-y-3">
        <h2 className="text-lg font-semibold">🔧 手动覆盖</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">节点 slug</label>
            <input value={overrideSlug} onChange={(e) => setOverrideSlug(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg text-sm" placeholder="rational-numbers" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">EF</label>
            <input value={overrideEF} onChange={(e) => setOverrideEF(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg text-sm" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">掌握度 (0-1)</label>
            <input value={overrideMastery} onChange={(e) => setOverrideMastery(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg text-sm" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">状态</label>
            <select value={overrideStatus} onChange={(e) => setOverrideStatus(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg text-sm">
              <option value="locked">locked</option>
              <option value="unlocked">unlocked</option>
              <option value="learning">learning</option>
              <option value="mastered">mastered</option>
              <option value="degraded">degraded</option>
            </select>
          </div>
        </div>
        <button onClick={handleOverride} className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm">执行覆盖</button>
      </section>

      {/* 3. Config + Reload */}
      <section className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800 space-y-3">
        <h2 className="text-lg font-semibold">⚡ 参数调节</h2>
        <div className="flex gap-3 items-end">
          <div>
            <label className="block text-xs text-gray-500 mb-1">参数路径</label>
            <input value={configParam} onChange={(e) => setConfigParam(e.target.value)}
              className="px-3 py-2 border rounded-lg text-sm w-48" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">新值</label>
            <input value={configValue} onChange={(e) => setConfigValue(e.target.value)}
              className="px-3 py-2 border rounded-lg text-sm w-32" />
          </div>
          <button onClick={handleConfigUpdate} className="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm">保存</button>
        </div>

        <div className="border-t pt-3 mt-3">
          <button onClick={handleReload} className="px-4 py-2 bg-gray-600 text-white rounded-lg text-sm">
            重新加载内容
          </button>
        </div>
      </section>
    </div>
  );
}
