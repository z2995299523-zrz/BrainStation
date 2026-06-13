"""SM-2 间隔重复算法（Anki 同款）"""
from datetime import date, timedelta
from typing import TypedDict


class SM2Result(TypedDict):
    ef: float
    interval: int
    repetitions: int
    next_review_at: str


def sm2_update(
    quality: int,
    ef: float = 2.5,
    interval: int = 0,
    repetitions: int = 0,
    skip_weekends: bool = True,
) -> SM2Result:
    """
    SM-2 算法

    参数:
        quality: 0-5
            5 = 完美
            4 = 正确，略有犹豫
            3 = 正确，但困难
            2 = 错误，但答案熟悉
            1 = 完全错误
            0 = 毫无记忆
        ef: 当前难易度因子 (初始 2.5)
        interval: 当前间隔天数
        repetitions: 连续正确次数
        skip_weekends: 跳过周六日

    返回:
        {ef, interval, repetitions, next_review_at}
    """
    if quality >= 3:
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 3
        else:
            new_interval = round(interval * ef)
        new_reps = repetitions + 1
    else:
        new_interval = 1
        new_reps = 0

    # 更新难易度因子
    new_ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(1.3, min(2.5, new_ef))

    # 计算下次复习日期
    next_date = date.today() + timedelta(days=new_interval)
    if skip_weekends:
        while next_date.weekday() >= 5:  # 周六=5, 周日=6
            next_date += timedelta(days=1)

    return {
        "ef": round(new_ef, 2),
        "interval": new_interval,
        "repetitions": new_reps,
        "next_review_at": next_date.isoformat(),
    }


def calculate_mastery(
    ef: float,
    repetitions: int,
    interval_days: int,
    last_study_at: str,
    mastery_threshold: float = 0.85,
) -> float:
    """计算掌握度 0.0~1.0，≥mastery_threshold 视为 mastered"""
    ef_weight = min(1.0, (ef - 1.3) / 1.2)      # EF 1.3→2.5 映射到 0→1
    rep_weight = min(1.0, repetitions / 5.0)      # 5次正确→满分

    # 衰减：超期未复习
    if last_study_at:
        days_since = (date.today() - date.fromisoformat(last_study_at)).days
    else:
        days_since = 0
    decay = max(0.7, 1.0 - 0.05 * max(0, days_since - interval_days))

    return round((ef_weight * 0.5 + rep_weight * 0.5) * decay, 3)
