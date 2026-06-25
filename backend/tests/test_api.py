"""API 集成测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import init_db, SessionLocal
from backend.config import config
from backend.models import User
import bcrypt
from jose import jwt
from datetime import datetime, timedelta, timezone


def _create_token(user_id: int) -> str:
    auth_config = config.auth
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    payload = {"user_id": user_id, "exp": expire}
    return jwt.encode(
        payload,
        auth_config.get("secret_key", ""),
        algorithm=auth_config.get("algorithm", "HS256"),
    )


@pytest.fixture
def client():
    """创建测试客户端，使用内存数据库（自动建表）"""
    init_db()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    """创建测试用户并返回带 token 的 headers"""
    db = SessionLocal()
    try:
        # 先检查是否已有测试用户
        user = db.query(User).filter(User.username == "_test_user_").first()
        if not user:
            user = User(
                username="_test_user_",
                hashed_password=bcrypt.hashpw(b"test1234", bcrypt.gensalt()).decode(),
                role="admin",
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        elif user.role != "admin":
            # 旧测试用户可能没有 role 或 role 不是 admin，需要更新
            user.role = "admin"
            db.commit()
            db.refresh(user)
        token = _create_token(user.id)
    finally:
        db.close()
    return {"Authorization": f"Bearer {token}"}


class TestHealthEndpoint:
    """健康检查（无需认证）"""

    def test_health_returns_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "nodes_loaded" in data
        assert "questions_loaded" in data


class TestAuthEndpoint:
    """认证 API"""

    def test_register_returns_token(self, client):
        import uuid
        uname = f"_test_reg_{uuid.uuid4().hex[:8]}"
        resp = client.post("/api/auth/register", json={
            "username": uname,
            "password": "test1234",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["username"] == uname

    def test_register_duplicate_returns_409(self, client):
        import uuid
        uname = f"_test_dup_{uuid.uuid4().hex[:8]}"
        # First registration succeeds
        client.post("/api/auth/register", json={
            "username": uname,
            "password": "test1234",
        })
        # Duplicate registration fails
        resp = client.post("/api/auth/register", json={
            "username": uname,
            "password": "test1234",
        })
        assert resp.status_code == 409

    def test_login_returns_token(self, client):
        import uuid
        uname = f"_test_login_{uuid.uuid4().hex[:8]}"
        pwd = "test1234"
        # Register first
        client.post("/api/auth/register", json={
            "username": uname,
            "password": pwd,
        })
        # Then login
        resp = client.post("/api/auth/login", json={
            "username": uname,
            "password": pwd,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    def test_login_wrong_password_returns_401(self, client):
        resp = client.post("/api/auth/login", json={
            "username": "_test_user_",
            "password": "wrong",
        })
        assert resp.status_code == 401

    def test_me_returns_user(self, client, auth_headers):
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "_test_user_"

    def test_me_without_token_returns_403(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 403


class TestContentEndpoint:
    """内容 API —— 章节内容读取 + 答题"""

    def test_get_chapter_returns_content(self, client, auth_headers):
        resp = client.get(
            "/api/content/chapter?slug=rational-numbers&stage=concept",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "rational-numbers"
        assert data["stage"] == "concept"
        assert "data" in data

    def test_get_chapter_invalid_slug_returns_404(self, client, auth_headers):
        resp = client.get(
            "/api/content/chapter?slug=nonexistent&stage=concept",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_get_chapter_practice_returns_questions(self, client, auth_headers):
        resp = client.get(
            "/api/content/chapter?slug=rational-numbers&stage=practice",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["stage"] == "practice"
        assert isinstance(data["data"], list)

    def test_submit_answer_returns_result(self, client, auth_headers):
        resp = client.post("/api/content/submit-answer", json={
            "chapter_slug": "rational-numbers",
            "question_id": "rat-prac-001",
            "user_answer": "-10",
            "difficulty": 1,
            "layer": "operation",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "is_correct" in data
        assert "correct_answer" in data
        assert "mastery_update" in data
        assert data["mastery_update"]["node_slug"] == "rational-numbers"

    def test_content_without_token_returns_403(self, client):
        resp = client.get("/api/content/chapter?slug=rational-numbers&stage=concept")
        assert resp.status_code == 403


class TestAIEndpoint:
    """AI API —— 提问 + 生成练习题"""

    def test_generate_practice_requires_valid_slug(self, client, auth_headers):
        resp = client.post("/api/ai/generate-practice", json={
            "chapter_slug": "nonexistent",
            "difficulty": 1,
            "count": 1,
        }, headers=auth_headers)
        assert resp.status_code == 404

    def test_ask_endpoint_exists(self, client, auth_headers):
        resp = client.post("/api/ai/ask", json={
            "chapter_slug": "rational-numbers",
            "current_stage": "concept",
            "current_position": "",
            "question": "什么是有理数？",
        }, headers=auth_headers)
        assert resp.status_code != 404


class TestProgressEndpoint:
    """进度 API"""

    def test_summary_returns_correct_structure(self, client, auth_headers):
        resp = client.get("/api/progress/summary", headers=auth_headers)
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

    def test_sm2_state_returns_nodes(self, client, auth_headers):
        resp = client.get("/api/admin/sm2-state", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "nodes" in data

    def test_reload_content(self, client, auth_headers):
        resp = client.post("/api/admin/reload-content", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "nodes_loaded" in data
