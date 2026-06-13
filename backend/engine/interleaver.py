"""交错题目生成器 —— 数学英语交错 + 按层抽样"""
import random
from typing import Any


def generate_daily_mix(
    all_questions: dict[str, list[dict]],  # {slug: [questions]}
    target_node: str,                      # 今天的新节点 slug
    due_review_nodes: list[str],           # 今天该复习的节点 slugs
    config: dict,                          # interleaving 配置
) -> dict[str, Any]:
    """
    生成一次训练的题目序列

    返回:
    {
        "warmup": [...],    # 预热题目列表
        "training": [...]   # 训练题目列表
    }
    """
    # === 预热检索 ===
    warmup_count = config["warmup"]["question_count"]  # 8
    deep_ratio = config["warmup"]["deep_question_ratio"]  # 0.2

    warmup_questions: list[dict] = []
    for slug in due_review_nodes:
        if len(warmup_questions) >= warmup_count:
            break
        qs = all_questions.get(slug, [])
        if qs:
            warmup_questions.append(random.choice(qs))

    # 注入深度题（理解层）
    deep_count = max(1, int(len(warmup_questions) * deep_ratio))
    for i in range(min(deep_count, len(warmup_questions))):
        slug = due_review_nodes[i] if i < len(due_review_nodes) else ""
        deep_qs = [
            q for q in all_questions.get(slug, [])
            if q.get("layer") == "understand"
        ]
        if deep_qs:
            warmup_questions[i] = random.choice(deep_qs)

    # 交错：数学一道 → 英语一道
    warmup_questions = _interleave(warmup_questions)

    # === 混合训练 ===
    train_count = config["training"]["question_count"]  # 14
    new_ratio = config["training"]["new_node_ratio"]    # 0.6

    new_count = int(train_count * new_ratio)
    old_count = train_count - new_count

    # 新节点题目（按层比例抽取）
    new_qs_all = all_questions.get(target_node, [])
    new_questions = _sample_by_layer(
        new_qs_all, new_count, config["training"]["new_node_layer_ratio"]
    )

    # 旧节点复习题目
    old_questions: list[dict] = []
    for slug in due_review_nodes[:5]:
        qs = all_questions.get(slug, [])
        if qs:
            old_questions.append(random.choice(qs))
    while len(old_questions) < old_count:
        if old_questions:
            old_questions.append(random.choice(old_questions))
        elif new_questions:
            old_questions.append(random.choice(new_questions))
        else:
            break

    training_questions = _interleave(new_questions + old_questions)

    # 变体注入
    variant_rate = config["training"].get("variant_injection_rate", 0)
    if variant_rate > 0:
        max_variants = config["training"].get("max_variant_per_session", 4)
        training_questions = _inject_variants(
            training_questions, variant_rate, max_variants
        )

    return {
        "warmup": warmup_questions,
        "training": training_questions,
    }


def _interleave(questions: list[dict]) -> list[dict]:
    """数学英语交错排列"""
    math_qs = [q for q in questions if q.get("subject") == "math"]
    eng_qs = [q for q in questions if q.get("subject") == "english"]
    result: list[dict] = []
    i, j = 0, 0
    toggle = True
    while i < len(math_qs) or j < len(eng_qs):
        if toggle and i < len(math_qs):
            result.append(math_qs[i])
            i += 1
        elif not toggle and j < len(eng_qs):
            result.append(eng_qs[j])
            j += 1
        else:
            # 一方耗尽，另一方补位
            if i < len(math_qs):
                result.append(math_qs[i])
                i += 1
            elif j < len(eng_qs):
                result.append(eng_qs[j])
                j += 1
        toggle = not toggle
    return result


def _sample_by_layer(
    questions: list[dict], count: int, ratios: dict[str, float]
) -> list[dict]:
    """按层比例抽样 (operation:0.6, understand:0.25, connect:0.15)"""
    result: list[dict] = []
    for layer, ratio in ratios.items():
        layer_qs = [q for q in questions if q.get("layer") == layer]
        n = max(1, int(count * ratio))
        sampled = random.sample(layer_qs, min(n, len(layer_qs))) if layer_qs else []
        result.extend(sampled)
    return result


def _inject_variants(
    questions: list[dict], rate: float, max_variants: int
) -> list[dict]:
    """注入变体题目——每 1/rate 题中 1 题用变体"""
    injected = 0
    step = max(1, int(1 / rate))
    for i in range(0, len(questions), step):
        if injected >= max_variants:
            break
        if i < len(questions) and questions[i].get("variants"):
            variant = random.choice(questions[i]["variants"])
            # 将变体内容合并为新题
            new_q = dict(questions[i])
            new_q["content"] = variant
            questions[i] = new_q
            injected += 1
    return questions
