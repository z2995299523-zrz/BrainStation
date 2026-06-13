"""交错调度器单元测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.engine.interleaver import _interleave, generate_daily_mix


def make_config():
    return {
        "warmup": {
            "question_count": 4,
            "deep_question_ratio": 0.2,
        },
        "training": {
            "question_count": 6,
            "new_node_ratio": 0.5,
            "new_node_layer_ratio": {
                "operation": 0.6,
                "understand": 0.25,
                "connect": 0.15,
            },
            "variant_injection_rate": 0.25,
            "max_variant_per_session": 2,
        },
    }


class TestInterleave:
    """交错排列测试"""

    def test_math_english_alternates(self):
        """1 数学 + 1 英语 → 交替排列"""
        questions = [
            {"id": "1", "subject": "math"},
            {"id": "2", "subject": "english"},
        ]
        result = _interleave(questions)
        subjects = [q["subject"] for q in result]
        # 应该交替出现
        assert subjects != ["math", "math"]
        assert subjects != ["english", "english"]
        assert len(result) == 2

    def test_only_math_no_crash(self):
        """只有数学、无英语 → 不崩溃，全数学"""
        questions = [
            {"id": "1", "subject": "math"},
            {"id": "2", "subject": "math"},
        ]
        result = _interleave(questions)
        assert len(result) == 2
        assert all(q["subject"] == "math" for q in result)

    def test_generate_daily_mix_returns_correct_structure(self):
        """generate_daily_mix 返回 warmup 和 training"""
        all_qs = {
            "target": [
                {"id": "t1", "subject": "math", "layer": "operation",
                 "content": {"stem": "test"}},
                {"id": "t2", "subject": "math", "layer": "understand",
                 "content": {"stem": "test"}},
                {"id": "t3", "subject": "math", "layer": "connect",
                 "content": {"stem": "test"}},
            ],
            "old1": [
                {"id": "o1", "subject": "english", "layer": "operation",
                 "content": {"stem": "test"}},
                {"id": "o2", "subject": "english", "layer": "understand",
                 "content": {"stem": "test"}},
                {"id": "o3", "subject": "english", "layer": "connect",
                 "content": {"stem": "test"}},
            ],
            "old2": [
                {"id": "o4", "subject": "math", "layer": "operation",
                 "content": {"stem": "test"}},
            ],
        }
        result = generate_daily_mix(
            all_qs, "target", ["old1", "old2"], make_config()
        )
        assert "warmup" in result
        assert "training" in result
        assert len(result["warmup"]) > 0
        assert len(result["training"]) > 0
