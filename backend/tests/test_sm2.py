"""SM-2 算法单元测试 —— 8 个用例"""
import pytest
from datetime import date, timedelta


# 直接导入被测函数（避免 backend 包导入问题）
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from backend.engine.sm2 import sm2_update, calculate_mastery


class TestSM2Update:
    """SM-2 核心算法测试"""

    def test_quality_5_perfect(self):
        """quality=5 完美 → ef 上升, interval 增长"""
        result = sm2_update(quality=5, ef=2.0, interval=10, repetitions=3,
                            skip_weekends=False)
        assert result["ef"] > 2.0  # EF 从 2.0 上升
        assert result["interval"] > 10  # 间隔增长
        assert result["repetitions"] == 4

    def test_quality_3_correct_hard(self):
        """quality=3 正确但困难 → ef 下降, interval=1(reset)"""
        result = sm2_update(quality=3, ef=2.0, interval=5, repetitions=2,
                            skip_weekends=False)
        assert result["ef"] < 2.0  # EF 下降
        assert result["repetitions"] == 3  # 仍算正确

    def test_quality_1_wrong(self):
        """quality=1 错误 → interval=1, reps=0"""
        result = sm2_update(quality=1, ef=2.5, interval=10, repetitions=3,
                            skip_weekends=False)
        assert result["interval"] == 1
        assert result["repetitions"] == 0

    def test_first_review(self):
        """quality=4, reps=0 → interval=1"""
        result = sm2_update(quality=4, ef=2.5, interval=0, repetitions=0,
                            skip_weekends=False)
        assert result["interval"] == 1
        assert result["repetitions"] == 1

    def test_second_review(self):
        """quality=4, reps=1 → interval=3"""
        result = sm2_update(quality=4, ef=2.5, interval=1, repetitions=1,
                            skip_weekends=False)
        assert result["interval"] == 3
        assert result["repetitions"] == 2

    def test_ef_clamping(self):
        """EF 最小值 1.3，最大值 2.5"""
        # 连续超低质量 → EF 触底 1.3
        r = sm2_update(quality=0, ef=1.35, interval=1, repetitions=0,
                       skip_weekends=False)
        assert r["ef"] >= 1.3

        # 连续高质量 → EF 不超过 2.5
        ef = 2.5
        for _ in range(10):
            r = sm2_update(quality=5, ef=ef, interval=10, repetitions=3,
                           skip_weekends=False)
            ef = r["ef"]
        assert ef <= 2.5

    def test_weekend_skip(self):
        """next_review_at 不落在周六日"""
        # 如果今天是周四，interval=1 → 周五，不用跳过
        today = date.today()
        result = sm2_update(quality=4, ef=2.5, interval=2, repetitions=1,
                            skip_weekends=True)
        next_date = date.fromisoformat(result["next_review_at"])
        assert next_date.weekday() < 5  # 不是周末

    def test_mastery_calculation(self):
        """验证 mastery 计算"""
        # 高 EF + 多次正确 + 刚学过 → 高掌握度
        m1 = calculate_mastery(ef=2.5, repetitions=5, interval_days=10,
                               last_study_at=date.today().isoformat())
        assert m1 >= 0.85  # 应 mastered

        # 低 EF + 无重复 + 未学过 → 低掌握度
        m2 = calculate_mastery(ef=1.3, repetitions=0, interval_days=0,
                               last_study_at=None)
        assert m2 < 0.5  # 很低

        # 长时间未复习 → 衰减
        old_date = (date.today() - timedelta(days=30)).isoformat()
        m3 = calculate_mastery(ef=2.5, repetitions=5, interval_days=10,
                               last_study_at=old_date)
        assert m3 < 1.0  # 有衰减
