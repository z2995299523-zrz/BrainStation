"""进度 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..config import config
from ..content.loader import ContentLoader
from ..database import get_db
from ..models import DailySession, UserProgress, ThoughtDiary

router = APIRouter(prefix="/api/progress", tags=["progress"])

_loader: ContentLoader | None = None


def get_loader() -> ContentLoader:
    global _loader
    if _loader is None:
        _loader = ContentLoader(config.app.get("content_dir", "./content"))
        _loader.load_all()
    return _loader


@router.get("/summary")
def get_summary(subject: str | None = None, db: Session = Depends(get_db)):
    """获取进度总览，可指定 subject=math 或 subject=english"""
    loader = get_loader()
    all_nodes_raw = loader.get_all_nodes()
    if subject:
        all_nodes = [n for n in all_nodes_raw if n.get("subject") == subject]
    else:
        all_nodes = all_nodes_raw
    total_nodes = len(all_nodes)

    progress_records = db.query(UserProgress).all()
    progress_map = {p.node_slug: p for p in progress_records}

    mastered = 0
    learning = 0
    unlocked_count = 0
    locked = 0

    nodes_data = []
    for node in all_nodes:
        slug = node["slug"]
        prog = progress_map.get(slug)
        if prog:
            status = prog.status
            mastery = prog.mastery_level
            ef = prog.ef
            next_review = prog.next_review_at
        else:
            # 检查前置是否满足
            from ..engine.mastery import get_unlocked_nodes
            unlocked_slugs = get_unlocked_nodes(all_nodes, progress_map)
            status = "unlocked" if slug in unlocked_slugs else "locked"
            mastery = 0.0
            ef = config.sm2.get("initial_ef", 2.5)
            next_review = None

        if status == "mastered":
            mastered += 1
        elif status in ("learning", "unlocked"):
            learning += 1
        elif status == "locked":
            locked += 1
        if status == "unlocked":
            unlocked_count += 1

        nodes_data.append({
            "slug": slug,
            "title": node.get("title", slug),
            "subject": node.get("subject", ""),
            "tier": node.get("tier", ""),
            "status": status,
            "mastery_level": mastery,
            "ef": ef,
            "next_review_at": next_review,
        })

    total_sessions = db.query(DailySession).count()
    completed_sessions = (
        db.query(DailySession)
        .filter(DailySession.status == "completed")
        .count()
    )

    # 计算连续打卡天数
    from datetime import date, timedelta
    today = date.today()
    streak = 0
    for i in range(365):
        check_date = (today - timedelta(days=i)).isoformat()
        sess = (
            db.query(DailySession)
            .filter(
                DailySession.session_date == check_date,
                DailySession.status == "completed",
            )
            .first()
        )
        if sess:
            streak += 1
        else:
            break

    # 总答题数
    from ..models import QuestionAttempt
    total_attempts = db.query(QuestionAttempt).count()
    correct_attempts = (
        db.query(QuestionAttempt)
        .filter(QuestionAttempt.is_correct == True)  # noqa: E712
        .count()
    )
    accuracy = (
        round(correct_attempts / total_attempts, 2)
        if total_attempts > 0
        else 0.0
    )

    return {
        "total_nodes": total_nodes,
        "mastered_nodes": mastered,
        "learning_nodes": learning,
        "unlocked_nodes": unlocked_count,
        "locked_nodes": locked,
        "streak_days": streak,
        "total_sessions": completed_sessions,
        "total_attempts": total_attempts,
        "overall_accuracy": accuracy,
        "nodes": nodes_data,
    }


@router.get("/tree")
def get_tree(subject: str | None = None, db: Session = Depends(get_db)):
    """获取掌握树状态，可指定 subject=math 或 subject=english"""
    loader = get_loader()
    all_nodes_raw = loader.get_all_nodes()
    if subject:
        all_nodes = [n for n in all_nodes_raw if n.get("subject") == subject]
    else:
        all_nodes = all_nodes_raw
    progress_records = db.query(UserProgress).all()
    progress_map = {p.node_slug: p for p in progress_records}

    from ..engine.mastery import get_unlocked_nodes
    unlocked = get_unlocked_nodes(
        all_nodes,
        progress_map,
        config.sm2.get("mastery_threshold", 0.85),
    )

    tree = {"math": [], "english": []}
    for node in all_nodes:
        slug = node["slug"]
        prog = progress_map.get(slug)
        status = (
            prog.status if prog
            else ("unlocked" if slug in unlocked else "locked")
        )
        subj = node.get("subject", "math")
        if subj in tree:
            tree[subj].append({
                "slug": slug,
                "title": node.get("title", slug),
                "status": status,
                "mastery": prog.mastery_level if prog else 0.0,
                "prerequisites": node.get("prerequisites", []),
            })

    return {"tree": tree, "unlocked_nodes": unlocked}


@router.get("/diary")
def get_diary(db: Session = Depends(get_db)):
    """获取思想日记列表（最近 3 条）"""
    diaries = (
        db.query(ThoughtDiary)
        .order_by(ThoughtDiary.created_at.desc())
        .limit(3)
        .all()
    )
    return [
        {
            "id": d.id,
            "session_date": d.session_date,
            "node_slug": d.node_slug,
            "reflection": d.reflection,
            "created_at": d.created_at,
        }
        for d in diaries
    ]
