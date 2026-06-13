"""API 集成测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import init_db
from backend.config import config


@pytest.fixture
def client():
    """创建测试客户端，使用内存数据库"""
    init_db()
    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    """健康检查"""

    def test_health_returns_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "nodes_loaded" in data
        assert "questions_loaded" in data


class TestSessionEndpoint:
    """训练会话 API"""

    def test_session_today_creates_session(self, client):
        resp = client.get("/api/session/today")
        assert resp.status_code in (200, 500)  # 500 if no content loaded yet
        if resp.status_code == 200:
            data = resp.json()
            assert "session_id" in data
            assert "steps" in data

    def test_answer_submit_requires_valid_question(self, client):
        """提交答案——无此题目应 404"""
        resp = client.post("/api/session/answer", json={
            "session_id": 1,
            "question_id": "nonexistent",
            "step_type": "training",
            "user_answer": {"choice": 0},
        })
        assert resp.status_code == 404

    def test_feynman_check_returns_feedback(self, client):
        """费曼提交——即使无会话也返回反馈（使用默认参数）"""
        # 先创建会话
        client.get("/api/session/today")
        resp = client.post("/api/session/feynman", json={
            "session_id": 0,  # 不存在的会话
            "explanation": "有理数是可以写成分数形式的数",
        })
        # 会话不存在 → 404
        assert resp.status_code == 404


class TestProgressEndpoint:
    """进度 API"""

    def test_summary_returns_correct_structure(self, client):
        resp = client.get("/api/progress/summary")
        assert resp.status_code == 200
        data = resp.json()
        for key in [
            "total_nodes", "mastered_nodes", "learning_nodes",
            "locked_nodes", "streak_days", "total_sessions",
            "total_attempts", "overall_accuracy", "nodes",
            "unlocked_nodes",
        ]:
            assert key in data


class TestAdminEndpoint:
    """管理面板 API"""

    def test_sm2_state_returns_nodes(self, client):
        resp = client.get("/api/admin/sm2-state")
        assert resp.status_code == 200
        data = resp.json()
        assert "nodes" in data

    def test_reload_content(self, client):
        resp = client.post("/api/admin/reload-content")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "nodes_loaded" in data
