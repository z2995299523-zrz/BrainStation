"""掌握树解析器单元测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.engine.mastery import get_unlocked_nodes


class FakeProgress:
    """模拟 UserProgress ORM 对象"""
    def __init__(self, slug, status="locked", mastery=0.0):
        self.node_slug = slug
        self.status = status
        self.mastery_level = mastery


def make_nodes():
    """构建测试用节点图：
        A(core,无前置) → B(core,前置A) → C(core,前置B)
    """
    return [
        {"slug": "A", "title": "节点A", "subject": "math", "tier": "core", "prerequisites": []},
        {"slug": "B", "title": "节点B", "subject": "math", "tier": "core", "prerequisites": ["A"]},
        {"slug": "C", "title": "节点C", "subject": "math", "tier": "core", "prerequisites": ["B"]},
    ]


class TestMastery:
    """掌握树测试"""

    def test_root_unlocked_when_all_locked(self):
        """无前置节点全部 locked → 根节点 unlocked"""
        nodes = make_nodes()
        # 所有节点都是 locked
        progress = {}
        unlocked = get_unlocked_nodes(nodes, progress)
        assert "A" in unlocked  # A 无前置，应被解锁

    def test_child_unlocked_when_parent_mastered(self):
        """A mastered → B(前置A) unlocked"""
        nodes = make_nodes()
        progress = {
            "A": FakeProgress("A", status="mastered", mastery=0.92),
        }
        unlocked = get_unlocked_nodes(nodes, progress)
        assert "B" in unlocked  # A 已 mastered，B 应解锁

    def test_not_unlocked_when_parent_learning(self):
        """前置仅 learning（未 mastered）→ 不解锁"""
        nodes = make_nodes()
        progress = {
            "A": FakeProgress("A", status="learning", mastery=0.5),
        }
        unlocked = get_unlocked_nodes(nodes, progress)
        assert "B" not in unlocked  # A 未 mastered，B 不解锁

    def test_both_prereqs_needed(self):
        """节点有两个前置，只 mastered 一个 → 不解锁"""
        nodes = [
            {"slug": "A", "prerequisites": []},
            {"slug": "B", "prerequisites": []},
            {"slug": "C", "prerequisites": ["A", "B"]},
        ]
        progress = {
            "A": FakeProgress("A", status="mastered", mastery=0.90),
            # B 不存在 → mastery = 0
        }
        unlocked = get_unlocked_nodes(nodes, progress)
        assert "C" not in unlocked  # 两个前置必须同时满足
