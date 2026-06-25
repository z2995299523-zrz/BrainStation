"""管理面板 API"""
import json
import secrets
import string
from datetime import datetime

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from ..config import config
from ..content.loader import ContentLoader
from ..database import get_db
from ..models import (
    UserProgress, ConfigChange, User,
    QuestionAttempt, DailySession, ThoughtDiary,
    Exam, ExamAttempt, ExamResult,
    ChatSession, ChatMessage,
)
from ..dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])

_loader: ContentLoader | None = None


def get_loader() -> ContentLoader:
    global _loader
    if _loader is None:
        _loader = ContentLoader(config.app.get("content_dir", "./content"))
        _loader.load_all()
    return _loader


class OverrideRequest(BaseModel):
    node_slug: str
    user_id: int | None = None  # 目标用户，None=当前管理员
    ef: float | None = None
    mastery_level: float | None = None
    status: str | None = None


class ConfigUpdateRequest(BaseModel):
    param_path: str
    new_value: str


VALID_ROLES = {"learner", "examiner", "admin"}


class UpdateRoleRequest(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def check_role(cls, v: str) -> str:
        if v not in VALID_ROLES:
            raise ValueError(f"无效角色: {v}，可选: {', '.join(sorted(VALID_ROLES))}")
        return v


class ResetPasswordRequest(BaseModel):
    new_password: str


@router.get("/sm2-state")
def get_sm2_state(
    user_id: int | None = Query(None, description="目标用户ID，不传则查当前管理员"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """查看指定用户的 SM-2 内部状态"""
    target_user_id = user_id if user_id is not None else current_user.id
    target_user = db.query(User).filter(User.id == target_user_id).first()
    loader = get_loader()
    all_nodes = loader.get_all_nodes()
    progress_records = db.query(UserProgress).filter(
        UserProgress.user_id == target_user_id
    ).all()
    progress_map = {p.node_slug: p for p in progress_records}

    result = []
    for node in all_nodes:
        slug = node["slug"]
        prog = progress_map.get(slug)
        result.append({
            "slug": slug,
            "title": node.get("title", slug),
            "subject": node.get("subject", ""),
            "tier": node.get("tier", ""),
            "mastery": prog.mastery_level if prog else 0.0,
            "ef": prog.ef if prog else config.sm2.get("initial_ef", 2.5),
            "interval": prog.interval_days if prog else 0,
            "repetitions": prog.repetitions if prog else 0,
            "next_review_at": prog.next_review_at if prog else None,
            "status": prog.status if prog else "locked",
            "total_attempts": prog.total_attempts if prog else 0,
            "correct_count": prog.correct_count if prog else 0,
        })

    return {
        "target_user": {
            "id": target_user.id if target_user else target_user_id,
            "username": target_user.username if target_user else str(target_user_id),
        },
        "nodes": result,
    }


@router.post("/sm2-override")
def override_sm2(
    req: OverrideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """手动覆盖节点状态"""
    target_user_id = req.user_id if req.user_id is not None else current_user.id
    prog = db.query(UserProgress).filter(
        UserProgress.user_id == target_user_id,
        UserProgress.node_slug == req.node_slug,
    ).first()

    if not prog:
        prog = UserProgress(
            user_id=target_user_id,
            node_slug=req.node_slug,
            status="learning",
            mastery_level=0.0,
            ef=config.sm2.get("initial_ef", 2.5),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        db.add(prog)

    old_values = {
        "ef": prog.ef,
        "mastery_level": prog.mastery_level,
        "status": prog.status,
    }

    if req.ef is not None:
        prog.ef = req.ef
    if req.mastery_level is not None:
        prog.mastery_level = req.mastery_level
    if req.status is not None:
        prog.status = req.status
    prog.updated_at = datetime.now().isoformat()

    # 记录变更
    change = ConfigChange(
        changed_at=datetime.now().isoformat(),
        param_path=f"progress.{req.node_slug}",
        old_value=json.dumps(old_values, ensure_ascii=False),
        new_value=json.dumps(
            {
                "ef": prog.ef,
                "mastery_level": prog.mastery_level,
                "status": prog.status,
            },
            ensure_ascii=False,
        ),
        note="管理员手动覆盖",
    )
    db.add(change)
    db.commit()

    return {"status": "ok", "node_slug": req.node_slug}


@router.post("/reload-content")
def reload_content(
    current_user: User = Depends(require_admin),
):
    """重新加载 YAML 内容"""
    loader = get_loader()
    loader.reload()
    nodes = len(loader.get_all_nodes())
    questions = sum(
        len(v) for v in loader.get_all_questions().values()
    )
    return {
        "status": "ok",
        "nodes_loaded": nodes,
        "questions_loaded": questions,
    }


@router.post("/config-update")
def update_config(
    req: ConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """运行时更新配置"""
    import yaml
    from pathlib import Path

    config_path = Path("config.yaml")
    if not config_path.exists():
        raise HTTPException(status_code=500, detail="config.yaml 不存在")

    # 读取当前配置
    with open(config_path, "r", encoding="utf-8") as f:
        current = yaml.safe_load(f)

    # 解析参数路径
    parts = req.param_path.split(".")
    target = current
    for part in parts[:-1]:
        if part not in target:
            target[part] = {}
        target = target[part]

    old_value = str(target.get(parts[-1], ""))
    # Parse value: handle bool, float, int, string
    raw = req.new_value
    if raw.lower() in ("true", "false"):
        parsed = raw.lower() == "true"
    elif raw.replace(".", "").replace("-", "").isdigit():
        parsed = float(raw) if "." in raw else int(raw)
    else:
        parsed = raw
    target[parts[-1]] = parsed

    # 写回
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(current, f, allow_unicode=True, default_flow_style=False)

    # 记录变更
    change = ConfigChange(
        changed_at=datetime.now().isoformat(),
        param_path=req.param_path,
        old_value=old_value,
        new_value=str(req.new_value),
        note="运行时更新",
    )
    db.add(change)
    db.commit()

    # 热重载
    config.reload()

    return {"status": "ok", "param": req.param_path, "value": req.new_value}


# ── 用户管理 ──


def _hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _generate_password(length: int = 12) -> str:
    """生成随机密码"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@router.get("/users")
def list_users(
    role: str | None = Query(None, description="按角色筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """获取所有用户列表（含学习统计）"""
    query = db.query(User)
    if role and role in VALID_ROLES:
        query = query.filter(User.role == role)

    users = query.order_by(User.created_at.desc()).all()

    result = []
    for u in users:
        progress_count = db.query(UserProgress).filter(
            UserProgress.user_id == u.id
        ).count()
        mastered_count = db.query(UserProgress).filter(
            UserProgress.user_id == u.id,
            UserProgress.status == "mastered",
        ).count()
        exam_count = db.query(ExamAttempt).filter(
            ExamAttempt.user_id == u.id
        ).count()

        result.append({
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "created_at": u.created_at,
            "progress_count": progress_count,
            "mastered_count": mastered_count,
            "exam_count": exam_count,
        })

    return {"users": result, "total": len(result)}


@router.get("/users/{user_id}")
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """获取单个用户详情"""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")

    progress_count = db.query(UserProgress).filter(
        UserProgress.user_id == user_id
    ).count()
    mastered_count = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.status == "mastered",
    ).count()
    exam_count = db.query(ExamAttempt).filter(
        ExamAttempt.user_id == user_id
    ).count()

    return {
        "user": {
            "id": target.id,
            "username": target.username,
            "role": target.role,
            "created_at": target.created_at,
            "progress_count": progress_count,
            "mastered_count": mastered_count,
            "exam_count": exam_count,
        }
    }


@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    req: UpdateRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """修改用户角色"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能修改自己的角色")

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")

    old_role = target.role
    target.role = req.role

    # 记录变更
    change = ConfigChange(
        changed_at=datetime.now().isoformat(),
        param_path=f"users.{target.username}.role",
        old_value=old_role,
        new_value=req.role,
        note=f"管理员 {current_user.username} 修改用户角色",
    )
    db.add(change)
    db.commit()

    return {
        "status": "ok",
        "user_id": user_id,
        "old_role": old_role,
        "new_role": req.role,
    }


@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    req: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """管理员重置用户密码"""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")

    target.hashed_password = _hash_pw(req.new_password)
    db.commit()

    return {
        "status": "ok",
        "user_id": user_id,
        "username": target.username,
        "message": f"用户 {target.username} 的密码已重置",
    }


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """删除用户及其所有关联数据"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")

    username = target.username

    # 级联删除关联数据（按依赖顺序）
    # 1. 聊天消息（通过 session 级联）
    chat_sessions = db.query(ChatSession).filter(
        ChatSession.user_id == user_id
    ).all()
    for cs in chat_sessions:
        db.query(ChatMessage).filter(
            ChatMessage.session_id == cs.id
        ).delete(synchronize_session=False)
        db.delete(cs)

    # 2. 考试相关
    db.query(ExamResult).filter(
        ExamResult.attempt_id.in_(
            db.query(ExamAttempt.id).filter(ExamAttempt.user_id == user_id)
        )
    ).delete(synchronize_session=False)
    db.query(ExamAttempt).filter(
        ExamAttempt.user_id == user_id
    ).delete(synchronize_session=False)
    # 该用户创建的考试：将 creator_id 置空（保留考试）
    db.query(Exam).filter(Exam.creator_id == user_id).update(
        {"creator_id": None}, synchronize_session=False
    )

    # 3. 其他记录
    db.query(ThoughtDiary).filter(
        ThoughtDiary.user_id == user_id
    ).delete(synchronize_session=False)
    db.query(DailySession).filter(
        DailySession.user_id == user_id
    ).delete(synchronize_session=False)
    db.query(QuestionAttempt).filter(
        QuestionAttempt.user_id == user_id
    ).delete(synchronize_session=False)
    db.query(UserProgress).filter(
        UserProgress.user_id == user_id
    ).delete(synchronize_session=False)

    # 4. 删除用户
    db.delete(target)
    db.commit()

    return {
        "status": "deleted",
        "user_id": user_id,
        "username": username,
        "message": f"用户 {username} 及其所有数据已删除",
    }


@router.get("/users/{user_id}/progress")
def get_user_progress(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """查看任意用户的学习进度"""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")

    loader = get_loader()
    all_nodes = loader.get_all_nodes()
    progress_records = db.query(UserProgress).filter(
        UserProgress.user_id == user_id
    ).all()
    progress_map = {p.node_slug: p for p in progress_records}

    nodes = []
    for node in all_nodes:
        slug = node["slug"]
        prog = progress_map.get(slug)
        nodes.append({
            "slug": slug,
            "title": node.get("title", slug),
            "subject": node.get("subject", ""),
            "tier": node.get("tier", ""),
            "status": prog.status if prog else "locked",
            "mastery": prog.mastery_level if prog else 0.0,
            "ef": prog.ef if prog else config.sm2.get("initial_ef", 2.5),
        })

    return {
        "user": {
            "id": target.id,
            "username": target.username,
            "role": target.role,
        },
        "nodes": nodes,
    }
