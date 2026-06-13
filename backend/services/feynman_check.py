"""费曼规则检查器 —— 关键词匹配 + 完整性评估"""

SYNONYMS: dict[str, list[str]] = {
    "拆成乘积": ["拆成", "乘积", "分解成", "乘法", "因式"],
    "用于解方程": ["解方程", "求出", "答案", "求解", "求根"],
    "和分解质因数类似": ["质因数", "质数", "分解", "小学", "类似"],
    "是乘法的逆运算": ["逆运算", "反过来", "逆向", "倒过来", "展开"],
    "直角边平方和": ["a²+b²", "a²+b²=c²", "两条直角边", "平方和"],
    "可用于求距离": ["距离", "长度", "求边长", "求斜边"],
}


def check_feynman(
    text: str,
    key_elements: list[str],
    missing_hints: dict[str, str],
    min_length: int = 20,
    min_match_ratio: float = 0.5,
) -> dict:
    """
    规则驱动费曼检查

    返回:
    {
        "quality_flag": "excellent" | "good" | "needs_work",
        "feedback": str,
        "completeness": float (0.0~1.0),
        "matched": [str],
        "missing": [str]
    }
    """
    text = text.strip()

    if len(text) < min_length:
        return {
            "quality_flag": "needs_work",
            "feedback": (
                f"💡 再写一点？至少 {min_length} 个字。"
                f"你现在写了 {len(text)} 个字。"
            ),
            "completeness": 0.0,
            "matched": [],
            "missing": key_elements,
        }

    matched: list[str] = []
    missing: list[str] = []

    for element in key_elements:
        keywords = SYNONYMS.get(element, [element])
        if any(kw in text for kw in keywords):
            matched.append(element)
        else:
            missing.append(element)

    ratio = len(matched) / len(key_elements) if key_elements else 0.0

    if ratio >= 0.8:
        flag = "excellent"
        feedback = f"✅ 解释很清晰！你已经抓住了核心：{'、'.join(matched)}。"
    elif ratio >= min_match_ratio:
        flag = "good"
        hint = missing_hints.get(
            missing[0] if missing else "",
            f"可以再想想'{missing[0]}'这个点" if missing else "",
        )
        feedback = (
            f"✅ 不错！你提到了 {'、'.join(matched)}。\n"
            f"💡 可以再想想：{hint}"
        )
    else:
        flag = "needs_work"
        hints = "\n".join(
            [f"• {missing_hints.get(m, m)}" for m in missing]
        )
        feedback = f"💡 再试试？以下是关键点提示：\n{hints}"

    return {
        "quality_flag": flag,
        "feedback": feedback,
        "completeness": round(ratio, 2),
        "matched": matched,
        "missing": missing,
    }
