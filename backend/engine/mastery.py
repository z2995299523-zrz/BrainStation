"""掌握树解析器 —— 判断节点解锁状态"""
from collections import defaultdict, deque


def get_unlocked_nodes(
    all_nodes: list[dict],       # [{slug, prerequisites: [str]}]
    progress_map: dict,          # {slug: UserProgress ORM}
    mastery_threshold: float = 0.85,
) -> list[str]:
    """
    解析掌握树：返回所有已解锁但未 mastered 的节点 slug 列表

    逻辑：
    1. 从无前置的根节点开始 BFS
    2. 检查节点的所有前置是否 >= mastery_threshold
    3. 满足条件 → 解锁该节点，将其子节点加入队列
    """
    node_map = {n["slug"]: n for n in all_nodes}
    children_of = defaultdict(list)   # parent_slug → [child_slugs]
    parents_of = defaultdict(list)    # child_slug → [parent_slugs]

    for node in all_nodes:
        slug = node["slug"]
        for prereq in node.get("prerequisites", []):
            children_of[prereq].append(slug)
            parents_of[slug].append(prereq)

    # 根节点：无前置的节点
    root_nodes = [n["slug"] for n in all_nodes if not n.get("prerequisites")]
    queue = deque(root_nodes)
    visited: set[str] = set()
    unlocked: list[str] = []

    while queue:
        slug = queue.popleft()
        if slug in visited:
            continue
        visited.add(slug)

        # 检查所有前置是否满足
        prereqs = parents_of.get(slug, [])
        all_prereqs_mastered = True
        for p_slug in prereqs:
            p_prog = progress_map.get(p_slug)
            p_mastery = getattr(p_prog, "mastery_level", 0) if p_prog else 0
            if p_mastery < mastery_threshold:
                all_prereqs_mastered = False
                break

        if all_prereqs_mastered:
            prog = progress_map.get(slug)
            status = getattr(prog, "status", "locked") if prog else "locked"
            if status == "locked":
                # 直接返回 slug（不自动改状态）
                unlocked.append(slug)
            elif status == "unlocked":
                unlocked.append(slug)

            # 子节点入队
            for child in children_of.get(slug, []):
                if child not in visited:
                    queue.append(child)

    return unlocked
