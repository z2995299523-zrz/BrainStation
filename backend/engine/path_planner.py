"""自适应路径规划 —— 推荐下一个要学的节点"""
from typing import Any


def recommend_next_node(
    all_nodes: list[dict],
    progress_map: dict,
    unlocked_slugs: list[str],
) -> dict[str, Any]:
    """
    推荐下一个要学的节点

    优先级：
    1. 未学的 core 节点
    2. 未学的 trunk 节点
    3. 学习中但掌握度 < 0.85
    4. 已退化的节点
    5. 未学的 extend 节点
    """
    unlearned_core: list[dict] = []
    unlearned_trunk: list[dict] = []
    unlearned_extend: list[dict] = []
    learning_low: list[tuple[dict, float]] = []
    degraded: list[tuple[dict, float]] = []

    for slug in unlocked_slugs:
        node = next((n for n in all_nodes if n["slug"] == slug), None)
        if not node:
            continue
        prog = progress_map.get(slug)
        mastery = getattr(prog, "mastery_level", 0) if prog else 0

        if not prog or getattr(prog, "status", "locked") == "unlocked":
            tier = node.get("tier", "core")
            if tier == "core":
                unlearned_core.append(node)
            elif tier == "trunk":
                unlearned_trunk.append(node)
            else:
                unlearned_extend.append(node)
        elif getattr(prog, "status", "") == "learning" and mastery < 0.85:
            learning_low.append((node, mastery))
        elif getattr(prog, "status", "") == "degraded":
            degraded.append((node, mastery))

    if unlearned_core:
        return {
            "slug": unlearned_core[0]["slug"],
            "reason": "核心节点，建议优先学习",
        }
    if unlearned_trunk:
        return {
            "slug": unlearned_trunk[0]["slug"],
            "reason": "主干节点，继续推进",
        }
    if learning_low:
        learning_low.sort(key=lambda x: x[1])
        return {
            "slug": learning_low[0][0]["slug"],
            "reason": "该节点学习中，继续巩固",
        }
    if degraded:
        degraded.sort(key=lambda x: x[1])
        return {
            "slug": degraded[0][0]["slug"],
            "reason": "该节点曾掌握但有所退化",
        }
    if unlearned_extend:
        return {
            "slug": unlearned_extend[0]["slug"],
            "reason": "扩展节点，可探索学习",
        }

    return {"slug": None, "reason": "所有节点已掌握"}
