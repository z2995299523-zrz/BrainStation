"""认证 API —— 注册、登录、当前用户"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import bcrypt
from jose import jwt

from ..config import config
from ..database import get_db
from ..models import User
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ── 请求/响应模型 ──


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=4, max_length=100, description="密码")


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: str


# ── 辅助函数 ──


def _create_token(user_id: int, role: str = "learner") -> str:
    """生成 JWT token，包含 user_id 和 role"""
    auth_config = config.auth
    expire_minutes = auth_config.get("token_expire_minutes", 1440)
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(
        payload,
        auth_config.get("secret_key", ""),
        algorithm=auth_config.get("algorithm", "HS256"),
    )


# ── 端点 ──


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """注册新用户"""
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已被注册",
        )

    # 创建用户（默认角色：learner）
    now = datetime.now(timezone.utc).isoformat()
    user = User(
        username=req.username,
        hashed_password=_hash_password(req.password),
        role="learner",
        created_at=now,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = _create_token(user.id, user.role)
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "username": user.username, "role": user.role},
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """登录"""
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    if not _verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token = _create_token(user.id, user.role)
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "username": user.username, "role": user.role},
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role or "learner",
        created_at=current_user.created_at or "",
    )
