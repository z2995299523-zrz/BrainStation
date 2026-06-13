"""管理面板 API"""
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config import config
from ..content.loader import ContentLoader
from ..database import get_db
from ..models import UserProgress, ConfigChange

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
    ef: float | None = None
    mastery_level: float | None = None
    status: str | None = None


class ConfigUpdateRequest(BaseModel):
    param_path: str
    new_value: str


@router.get("/sm2-state")
def get_sm2_state(db: Session = Depends(get_db)):
    """查看所有节点的 SM-2 内部状态"""
    loader = get_loader()
    all_nodes = loader.get_all_nodes()
    progress_records = db.query(UserProgress).all()
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

    return {"nodes": result}


@router.post("/sm2-override")
def override_sm2(req: OverrideRequest, db: Session = Depends(get_db)):
    """手动覆盖节点状态"""
    prog = db.query(UserProgress).filter(
        UserProgress.node_slug == req.node_slug
    ).first()

    if not prog:
        prog = UserProgress(
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
def reload_content():
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
def update_config(req: ConfigUpdateRequest, db: Session = Depends(get_db)):
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
