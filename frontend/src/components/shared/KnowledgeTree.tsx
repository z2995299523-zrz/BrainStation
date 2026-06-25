import { useMemo } from 'react';
import type { TreeNodeData, NodeProgress } from '../../types';

interface Props {
  nodes: NodeProgress[];
  subject?: 'math' | 'english';
}

function buildTree(nodes: NodeProgress[]): { roots: TreeNodeData[]; childrenMap: Record<string, TreeNodeData[]> } {
  const childrenMap: Record<string, TreeNodeData[]> = {};
  const nodeMap: Record<string, TreeNodeData> = {};
  const roots: TreeNodeData[] = [];

  // First pass: create TreeNodeData for each node
  for (const n of nodes) {
    const treeNode: TreeNodeData = {
      slug: n.slug,
      title: n.title,
      status: n.status,
      mastery: n.mastery_level,
      prerequisites: n.prerequisites || [],
    };
    nodeMap[n.slug] = treeNode;
  }

  // Second pass: build parent-child relationships
  for (const n of nodes) {
    const treeNode = nodeMap[n.slug];
    const prereqs = n.prerequisites || [];

    if (prereqs.length === 0) {
      roots.push(treeNode);
    } else {
      for (const pre of prereqs) {
        if (!childrenMap[pre]) childrenMap[pre] = [];
        childrenMap[pre].push(treeNode);
      }
    }
  }

  return { roots, childrenMap };
}

const STATUS_CONFIG: Record<string, { icon: string; color: string; bg: string }> = {
  mastered: { icon: '✅', color: 'text-green-700 dark:text-green-300', bg: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' },
  learning: { icon: '📖', color: 'text-blue-700 dark:text-blue-300', bg: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800' },
  unlocked: { icon: '🔓', color: 'text-amber-700 dark:text-amber-300', bg: 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800' },
  locked: { icon: '🔒', color: 'text-gray-400 dark:text-gray-500', bg: 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700' },
};

function TreeNodeItem({ node, childrenMap, depth = 0 }: { node: TreeNodeData; childrenMap: Record<string, TreeNodeData[]>; depth?: number }) {
  const children = childrenMap[node.slug] || [];
  const config = STATUS_CONFIG[node.status] || STATUS_CONFIG.locked;
  const masteryPercent = Math.round((node.mastery || 0) * 100);

  return (
    <li className="tree-leaf">
      <div
        className={`tree-node-card inline-flex items-center gap-3 px-3 py-2 rounded-xl border ${config.bg} transition-all min-w-[200px]`}
      >
        <span className="text-lg flex-shrink-0">{config.icon}</span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className={`text-sm font-semibold truncate ${config.color}`}>{node.title}</span>
            {node.status === 'locked' && (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-200 dark:bg-gray-600 text-gray-500 dark:text-gray-400">
                未解锁
              </span>
            )}
          </div>
          {node.status !== 'locked' && (
            <div className="flex items-center gap-2 mt-1">
              <div className="flex-1 h-1.5 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden max-w-[100px]">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${masteryPercent}%`,
                    backgroundColor:
                      masteryPercent >= 85 ? '#22c55e' : masteryPercent >= 50 ? '#f59e0b' : '#3b82f6',
                  }}
                />
              </div>
              <span className="text-[10px] text-gray-400 dark:text-gray-500">{masteryPercent}%</span>
            </div>
          )}
        </div>
      </div>

      {children.length > 0 && (
        <ul className="tree-branch">
          {children.map((child) => (
            <TreeNodeItem key={child.slug} node={child} childrenMap={childrenMap} depth={depth + 1} />
          ))}
        </ul>
      )}
    </li>
  );
}

export default function KnowledgeTree({ nodes }: Props) {
  const { roots, childrenMap } = useMemo(() => buildTree(nodes), [nodes]);

  // Stats
  const total = nodes.length;
  const mastered = nodes.filter((n) => n.status === 'mastered').length;
  const learning = nodes.filter((n) => n.status === 'learning').length;
  const unlocked = nodes.filter((n) => n.status === 'unlocked').length;

  if (total === 0) {
    return (
      <div className="text-center py-8 text-gray-400 dark:text-gray-500">
        <p className="text-4xl mb-2">🌱</p>
        <p className="text-sm">还没有学习节点数据</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Stats bar */}
      <div className="flex gap-3 text-xs text-gray-500 dark:text-gray-400 flex-wrap">
        <span>📊 总计 {total}</span>
        <span className="text-green-600 dark:text-green-400">✅ {mastered} 已掌握</span>
        <span className="text-blue-600 dark:text-blue-400">📖 {learning} 学习中</span>
        {unlocked > 0 && (
          <span className="text-amber-600 dark:text-amber-400">🔓 {unlocked} 待解锁</span>
        )}
      </div>

      {/* Tree */}
      <div className="tree-root">
        <ul>
          {roots.map((root) => (
            <TreeNodeItem key={root.slug} node={root} childrenMap={childrenMap} />
          ))}
        </ul>
      </div>

      {/* Orphan nodes (shouldn't happen often, but display them) */}
      {roots.length === 0 && (
        <ul className="tree-branch">
          {nodes.map((n) => (
            <TreeNodeItem
              key={n.slug}
              node={{
                slug: n.slug,
                title: n.title,
                status: n.status,
                mastery: n.mastery_level,
                prerequisites: n.prerequisites || [],
              }}
              childrenMap={{}}
            />
          ))}
        </ul>
      )}
    </div>
  );
}
