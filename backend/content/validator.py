"""内容完整性校验器"""
from collections import defaultdict
from typing import Any


def validate_content(loader) -> dict[str, list[str]]:
    """
    校验所有已加载内容的完整性

    检查项：
    1. 所有引用的 prerequisites 都存在
    2. 所有节点有必需的三个内容层级 (operation/understand/connect)
    3. 每道题有必需的字段 (id, layer, q_type, content, answer)
    4. 无循环依赖

    返回: {"errors": [...], "warnings": [...]}
    """
    errors: list[str] = []
    warnings: list[str] = []
    all_nodes = loader.get_all_nodes()
    node_map = {n["slug"]: n for n in all_nodes}
    all_slugs = set(node_map.keys())

    # 1. 检查前置依赖引用
    for node in all_nodes:
        slug = node["slug"]
        prereqs = node.get("prerequisites", [])
        for p in prereqs:
            if p not in all_slugs:
                errors.append(f"节点 '{slug}' 的前置 '{p}' 不存在")

    # 2. 检查每个节点的完整内容结构
    for slug in all_slugs:
        full_node = loader.get_node(slug)
        if full_node:
            content = full_node.get("content", {})
            for layer in ["operation", "understand", "connect"]:
                if layer not in content:
                    errors.append(f"节点 '{slug}' 缺少内容层: {layer}")
                elif not content[layer].get("text"):
                    errors.append(f"节点 '{slug}' 的 '{layer}' 层的 text 为空")

    # 3. 检查题目完整性
    all_questions = loader.get_all_questions()
    total_questions = 0
    for slug, questions in all_questions.items():
        if slug not in all_slugs:
            errors.append(f"题目引用的节点 '{slug}' 不存在")
        for q in questions:
            total_questions += 1
            qid = q.get("id", "?")
            for field in ["id", "layer", "q_type", "content", "answer"]:
                if field not in q:
                    errors.append(f"题目 '{qid}' (节点 {slug}) 缺少字段: {field}")
            # 选择题必须有 options
            if q.get("q_type") == "choice" and "options" not in q.get("content", {}):
                errors.append(f"选择题 '{qid}' (节点 {slug}) 缺少 options")

    # 4. 检查循环依赖 (DFS)
    if _has_cycle(node_map):
        errors.append("知识节点存在循环依赖")

    # 5. 每个节点至少 8 题（警告）
    for slug in all_slugs:
        count = len(all_questions.get(slug, []))
        if count < 8:
            warnings.append(f"节点 '{slug}' 仅 {count} 题（建议 >= 8）")

    return {"errors": errors, "warnings": warnings}


def _has_cycle(node_map: dict[str, dict]) -> bool:
    """DFS 检测有向图中的环"""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = defaultdict(int)

    def dfs(slug: str) -> bool:
        color[slug] = GRAY
        for prereq in node_map.get(slug, {}).get("prerequisites", []):
            if prereq not in node_map:
                continue
            if color[prereq] == GRAY:
                return True  # 发现环
            if color[prereq] == WHITE:
                if dfs(prereq):
                    return True
        color[slug] = BLACK
        return False

    for slug in node_map:
        if color[slug] == WHITE:
            if dfs(slug):
                return True
    return False
