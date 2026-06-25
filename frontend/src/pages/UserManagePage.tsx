import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { UserManageItem } from '../types';

type RoleFilter = 'all' | 'learner' | 'examiner' | 'admin';

const ROLE_BADGE_COLORS: Record<string, string> = {
  learner: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  examiner: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  admin: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400',
};

export default function UserManagePage() {
  const [users, setUsers] = useState<UserManageItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [roleFilter, setRoleFilter] = useState<RoleFilter>('all');
  const [msg, setMsg] = useState('');
  const [error, setError] = useState('');
  const [expandedUser, setExpandedUser] = useState<number | null>(null);
  const [userProgress, setUserProgress] = useState<Array<Record<string, unknown>>>([]);
  const [progressLoading, setProgressLoading] = useState(false);

  // Password reset state
  const [resetModalOpen, setResetModalOpen] = useState(false);
  const [resetUserId, setResetUserId] = useState<number | null>(null);
  const [resetUsername, setResetUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [resetError, setResetError] = useState('');

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await api.getUsers(roleFilter === 'all' ? undefined : roleFilter);
      setUsers((data.users as unknown as UserManageItem[]) ?? []);
      setError('');
    } catch (e) {
      setError((e as Error).message || '加载用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [roleFilter]);

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      const result = await api.updateUserRole(userId, newRole);
      setMsg(`角色已更新: ${(result as Record<string, unknown>).old_role} → ${newRole}`);
      setError('');
      fetchUsers();
    } catch (e) {
      setError((e as Error).message || '修改角色失败');
    }
  };

  const openResetModal = (userId: number, username: string) => {
    setResetUserId(userId);
    setResetUsername(username);
    setNewPassword('');
    setResetError('');
    setResetModalOpen(true);
  };

  const handleResetPassword = async () => {
    if (!resetUserId || !newPassword) {
      setResetError('请输入新密码');
      return;
    }
    if (newPassword.length < 4) {
      setResetError('密码至少 4 位');
      return;
    }
    try {
      await api.resetUserPassword(resetUserId, newPassword);
      setMsg(`用户 ${resetUsername} 密码已重置`);
      setResetModalOpen(false);
      setError('');
    } catch (e) {
      setResetError((e as Error).message || '重置密码失败');
    }
  };

  const handleDeleteUser = async (userId: number, username: string) => {
    if (!confirm(`确定删除用户「${username}」？\n\n该操作将删除该用户的所有学习记录、考试记录、聊天记录等数据，且不可撤销。`)) {
      return;
    }
    try {
      await api.deleteUser(userId);
      setMsg(`用户「${username}」已删除`);
      setError('');
      fetchUsers();
    } catch (e) {
      setError((e as Error).message || '删除用户失败');
    }
  };

  const handleViewProgress = async (userId: number) => {
    if (expandedUser === userId) {
      setExpandedUser(null);
      setUserProgress([]);
      return;
    }
    setExpandedUser(userId);
    setProgressLoading(true);
    try {
      const data = await api.getUserProgress(userId);
      setUserProgress((data.nodes as Array<Record<string, unknown>>) ?? []);
    } catch (e) {
      setError((e as Error).message || '加载进度失败');
    } finally {
      setProgressLoading(false);
    }
  };

  const statusBadge = (status: string) => {
    const colors: Record<string, string> = {
      mastered: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      learning: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
      unlocked: 'bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400',
      locked: 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400',
      degraded: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400',
    };
    const labels: Record<string, string> = {
      mastered: '已掌握',
      learning: '学习中',
      unlocked: '已解锁',
      locked: '未解锁',
      degraded: '已退化',
    };
    return (
      <span className={`text-xs px-1.5 py-0.5 rounded ${colors[status] || colors.locked}`}>
        {labels[status] || status}
      </span>
    );
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
          👥 用户管理
          {!loading && (
            <span className="ml-3 text-sm font-normal text-gray-400">
              共 {users.length} 人
            </span>
          )}
        </h1>
      </div>

      {/* Messages */}
      {msg && (
        <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-sm text-green-700 dark:text-green-400">
          ✅ {msg}
          <button onClick={() => setMsg('')} className="ml-2 text-green-500 hover:text-green-700">✕</button>
        </div>
      )}
      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-600 dark:text-red-400">
          ❌ {error}
          <button onClick={() => setError('')} className="ml-2 text-red-500 hover:text-red-700">✕</button>
        </div>
      )}

      {/* Role filter tabs */}
      <div className="flex gap-2 flex-wrap">
        {([
          ['all', '全部'],
          ['learner', '👨‍🎓 学习者'],
          ['examiner', '📝 考核者'],
          ['admin', '⚙️ 管理员'],
        ] as [RoleFilter, string][]).map(([val, label]) => (
          <button
            key={val}
            onClick={() => setRoleFilter(val)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              roleFilter === val
                ? 'bg-indigo-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-750'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* User table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin h-8 w-8 border-b-2 border-indigo-600 rounded-full" />
          </div>
        ) : users.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <p className="text-3xl mb-2">📭</p>
            <p>暂无用户</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 text-left">
                  <th className="p-3 pl-4 font-medium text-gray-500 dark:text-gray-400 w-8">#</th>
                  <th className="p-3 font-medium text-gray-500 dark:text-gray-400">用户名</th>
                  <th className="p-3 font-medium text-gray-500 dark:text-gray-400">角色</th>
                  <th className="p-3 font-medium text-gray-500 dark:text-gray-400">注册时间</th>
                  <th className="p-3 font-medium text-gray-500 dark:text-gray-400">学习进度</th>
                  <th className="p-3 font-medium text-gray-500 dark:text-gray-400">考试</th>
                  <th className="p-3 pr-4 font-medium text-gray-500 dark:text-gray-400">操作</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u, idx) => (
                  <>
                    <tr
                      key={u.id}
                      className={`border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors ${
                        expandedUser === u.id ? 'bg-indigo-50/50 dark:bg-indigo-900/10' : ''
                      }`}
                    >
                      <td className="p-3 pl-4 text-gray-400 text-xs">{idx + 1}</td>
                      <td className="p-3 font-medium text-gray-800 dark:text-gray-200">
                        {u.username}
                      </td>
                      <td className="p-3">
                        <select
                          value={u.role}
                          onChange={(e) => handleRoleChange(u.id, e.target.value)}
                          className={`text-xs px-2 py-1 rounded-full border-0 font-medium cursor-pointer ${
                            ROLE_BADGE_COLORS[u.role] || ROLE_BADGE_COLORS.learner
                          }`}
                          style={{ appearance: 'auto' }}
                        >
                          <option value="learner">学习者</option>
                          <option value="examiner">考核者</option>
                          <option value="admin">管理员</option>
                        </select>
                      </td>
                      <td className="p-3 text-xs text-gray-500 dark:text-gray-400">
                        {u.created_at ? u.created_at.slice(0, 10) : '-'}
                      </td>
                      <td className="p-3 text-xs text-gray-500 dark:text-gray-400">
                        <button
                          onClick={() => handleViewProgress(u.id)}
                          className="hover:text-indigo-600 transition-colors"
                        >
                          {u.mastered_count}/{u.progress_count}
                          {u.progress_count > 0 && (
                            <span className="ml-1 text-gray-400">
                              ({Math.round((u.mastered_count / u.progress_count) * 100)}%)
                            </span>
                          )}
                        </button>
                      </td>
                      <td className="p-3 text-xs text-gray-500 dark:text-gray-400">
                        {u.exam_count > 0 ? `${u.exam_count} 次` : '-'}
                      </td>
                      <td className="p-3 pr-4">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => openResetModal(u.id, u.username)}
                            className="text-xs px-2 py-1 text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-colors"
                          >
                            🔑 密码
                          </button>
                          <button
                            onClick={() => handleDeleteUser(u.id, u.username)}
                            className="text-xs px-2 py-1 text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                          >
                            🗑 删除
                          </button>
                        </div>
                      </td>
                    </tr>
                    {/* Expanded progress row */}
                    {expandedUser === u.id && (
                      <tr key={`${u.id}-progress`}>
                        <td colSpan={7} className="p-0">
                          <div className="bg-gray-50 dark:bg-gray-750 px-4 py-3 border-t border-gray-100 dark:border-gray-700">
                            {progressLoading ? (
                              <div className="flex justify-center py-4">
                                <div className="animate-spin h-5 w-5 border-b-2 border-indigo-600 rounded-full" />
                              </div>
                            ) : userProgress.length === 0 ? (
                              <p className="text-sm text-gray-400 py-2">暂无学习记录</p>
                            ) : (
                              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 max-h-64 overflow-y-auto">
                                {userProgress.map((node) => (
                                  <div
                                    key={node.slug as string}
                                    className="flex items-center justify-between bg-white dark:bg-gray-800 rounded-lg px-3 py-2 text-xs border border-gray-100 dark:border-gray-700"
                                  >
                                    <span className="text-gray-700 dark:text-gray-300 truncate mr-2">
                                      {node.title as string}
                                    </span>
                                    {statusBadge(node.status as string)}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Password Reset Modal */}
      {resetModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 w-full max-w-md shadow-xl">
            <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-2">
              🔑 重置密码
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              用户: <strong>{resetUsername}</strong>
            </p>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                新密码
              </label>
              <input
                type="text"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="输入新密码 (至少4位)"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-sm"
                onKeyDown={(e) => e.key === 'Enter' && handleResetPassword()}
                autoFocus
              />
            </div>

            {resetError && (
              <p className="text-sm text-red-500 mb-3">❌ {resetError}</p>
            )}

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setResetModalOpen(false)}
                className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleResetPassword}
                className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                确认重置
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
