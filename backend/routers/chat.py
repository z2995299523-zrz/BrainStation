"""聊天会话 API —— 会话 CRUD + 消息持久化"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..config import config
from ..database import get_db
from ..models import User, ChatSession, ChatMessage
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ── 请求/响应模型 ──


class CreateSessionRequest(BaseModel):
    chapter_slug: str
    title: str = "新对话"


class SaveMessagesRequest(BaseModel):
    messages: list[dict] = Field(default_factory=list)


class SessionResponse(BaseModel):
    id: int
    chapter_slug: str
    title: str
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: str


# ── 端点 ──


@router.get("/sessions")
def list_sessions(
    chapter_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取某章节的所有会话（最新在前）"""
    sessions = (
        db.query(ChatSession)
        .filter(
            ChatSession.user_id == current_user.id,
            ChatSession.chapter_slug == chapter_slug,
        )
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "chapter_slug": s.chapter_slug,
            "title": s.title,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        for s in sessions
    ]


@router.post("/sessions")
def create_session(
    req: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建新会话"""
    now = datetime.now(timezone.utc).isoformat()
    session = ChatSession(
        user_id=current_user.id,
        chapter_slug=req.chapter_slug,
        title=req.title,
        created_at=now,
        updated_at=now,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "id": session.id,
        "chapter_slug": session.chapter_slug,
        "title": session.title,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除会话及其所有消息"""
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    # 先删消息
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    db.delete(session)
    db.commit()
    return {"status": "ok"}


@router.get("/sessions/{session_id}/messages")
def get_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取会话的所有消息"""
    # 验证会话属于当前用户
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return [
        {
            "id": m.id,
            "session_id": m.session_id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at,
        }
        for m in messages
    ]


@router.post("/sessions/{session_id}/messages")
def save_messages(
    session_id: int,
    req: SaveMessagesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """保存消息到会话（覆盖式：先清空再写入）"""
    # 验证会话属于当前用户
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    now = datetime.now(timezone.utc).isoformat()

    # 清空旧消息
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()

    # 写入新消息
    for msg in req.messages:
        if msg.get("content") and msg.get("role") in ("user", "assistant"):
            m = ChatMessage(
                session_id=session_id,
                role=msg["role"],
                content=msg["content"],
                created_at=now,
            )
            db.add(m)

    # 更新会话时间
    session.updated_at = now
    # 自动用第一条用户消息作为标题
    first_user_msg = next(
        (m for m in req.messages if m.get("role") == "user" and m.get("content")),
        None,
    )
    if first_user_msg:
        title = first_user_msg["content"][:30]
        session.title = title if len(title) < 30 else title + "..."

    db.commit()
    return {"status": "ok", "count": len(req.messages)}
