"""训练 API —— 6 步训练流"""
import json
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config import config
from ..content.loader import ContentLoader
from ..database import get_db
from ..engine.session_builder import SessionBuilder
from ..engine.sm2 import sm2_update, calculate_mastery
from ..models import DailySession, QuestionAttempt, UserProgress, ThoughtDiary
from ..services.feynman_check import check_feynman

router = APIRouter(prefix="/api/session", tags=["session"])

# 内容加载器（单例）
_loader: ContentLoader | None = None


def get_loader() -> ContentLoader:
    global _loader
    if _loader is None:
        content_dir = config.app.get("content_dir", "./content")
        _loader = ContentLoader(content_dir)
        _loader.load_all()
    return _loader


# ── 请求体模型 ──

class AnswerRequest(BaseModel):
    session_id: int
    question_id: str
    step_type: str  # "warmup" | "training"
    user_answer: dict | str | None = None
    confidence: int = 3  # 1-5
    time_spent_sec: int = 0


class FeynmanRequest(BaseModel):
    session_id: int
    explanation: str
    deep_choice: str | None = None  # "A" | "B"
    deep_answer: str | None = None


class CalibrateRequest(BaseModel):
    session_id: int
    confidence: int  # 1-5
    thought_diary: str = ""


class CompleteRequest(BaseModel):
    session_id: int
    total_time_sec: int = 0


# ── 端点 ──

@router.get("/today")
def get_today(subject: str | None = None, db: Session = Depends(get_db)):
    """获取今天的训练内容（6 步全量数据），可指定 subject=math 或 subject=english"""
    loader = get_loader()
    builder = SessionBuilder(loader)
    try:
        result = builder.build_session(db, subject=subject)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer")
def submit_answer(req: AnswerRequest, db: Session = Depends(get_db)):
    """提交单题答案（warmup 或 training）"""
    loader = get_loader()
    question = None
    for qs in loader.get_all_questions().values():
        for q in qs:
            if q.get("id") == req.question_id:
                question = q
                break
        if question:
            break

    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    # 判断正误
    answer = question.get("answer", {})
    correct = answer.get("correct") if answer else None
    explanation = answer.get("explanation", "") if answer else ""

    if question.get("q_type") == "choice":
        if isinstance(req.user_answer, dict):
            is_correct = req.user_answer.get("choice") == correct
        else:
            is_correct = req.user_answer == correct
    elif question.get("q_type") == "fill":
        correct_str = str(correct) if correct is not None else ""
        user_str = str(req.user_answer) if req.user_answer else ""
        is_correct = user_str.strip().lower() == correct_str.strip().lower()
    else:
        # open/explain: 不自动判对错，记录即可
        is_correct = None

    # 质量分：对=4，错=1，不评分=3
    if is_correct is True:
        quality = 4
    elif is_correct is False:
        quality = 1
    else:
        quality = 3

    # 找到对应的 node_slug
    node_slug = question.get("node_slug", "")
    # 从 loader 查找（题目本身可能没有 node_slug，从所属文件找）
    if not node_slug:
        for slug, qs in loader.get_all_questions().items():
            if question in qs:
                node_slug = slug
                break

    # 更新 SM-2 状态
    progress = db.query(UserProgress).filter(
        UserProgress.node_slug == node_slug
    ).first()

    mastery_before = progress.mastery_level if progress else 0.0

    if progress:
        result = sm2_update(
            quality=quality,
            ef=progress.ef,
            interval=progress.interval_days,
            repetitions=progress.repetitions,
            skip_weekends=config.sm2.get("skip_weekends", True),
        )
        progress.ef = result["ef"]
        progress.interval_days = result["interval"]
        progress.repetitions = result["repetitions"]
        progress.next_review_at = result["next_review_at"]
        progress.total_attempts += 1
        if is_correct:
            progress.correct_count += 1
        progress.last_study_at = date.today().isoformat()
        progress.updated_at = date.today().isoformat()

        # 更新状态
        new_mastery = calculate_mastery(
            progress.ef,
            progress.repetitions,
            progress.interval_days,
            progress.last_study_at,
            config.sm2.get("mastery_threshold", 0.85),
        )
        progress.mastery_level = new_mastery
        if new_mastery >= config.sm2.get("mastery_threshold", 0.85):
            progress.status = "mastered"
        elif progress.status == "locked":
            progress.status = "learning"
        elif progress.status in ("unlocked", "mastered"):
            progress.status = "learning"
    else:
        prog = UserProgress(
            node_slug=node_slug,
            status="learning",
            mastery_level=0.0,
            ef=config.sm2.get("initial_ef", 2.5),
            total_attempts=1,
            correct_count=1 if is_correct else 0,
            last_study_at=date.today().isoformat(),
            created_at=date.today().isoformat(),
            updated_at=date.today().isoformat(),
        )
        result = sm2_update(
            quality=quality,
            skip_weekends=config.sm2.get("skip_weekends", True),
        )
        prog.ef = result["ef"]
        prog.interval_days = result["interval"]
        prog.repetitions = result["repetitions"]
        prog.next_review_at = result["next_review_at"]
        db.add(prog)

    # 记录答题
    attempt = QuestionAttempt(
        node_slug=node_slug,
        question_id=req.question_id,
        session_id=req.session_id,
        user_answer=json.dumps(req.user_answer, ensure_ascii=False)
        if req.user_answer else None,
        is_correct=is_correct,
        quality_score=quality,
        confidence=req.confidence,
        time_spent_sec=req.time_spent_sec,
        created_at=datetime.now().isoformat(),
    )
    db.add(attempt)

    # 更新会话的 steps_data
    session = db.query(DailySession).filter(
        DailySession.id == req.session_id
    ).first()
    if session:
        steps = json.loads(session.steps_data or "{}")
        step_key = req.step_type
        if step_key not in steps:
            steps[step_key] = []
        steps[step_key].append(req.question_id)
        session.steps_data = json.dumps(steps, ensure_ascii=False)

    db.commit()

    # 获取更新后的 mastery
    mastery_after = 0.0
    if progress:
        progress_obj = db.query(UserProgress).filter(
            UserProgress.node_slug == node_slug
        ).first()
        if progress_obj:
            mastery_after = progress_obj.mastery_level

    return {
        "is_correct": is_correct,
        "explanation": explanation,
        "mastery_update": {
            "node_slug": node_slug,
            "mastery_before": round(mastery_before, 3),
            "mastery_after": round(mastery_after, 3),
            "new_ef": result["ef"],
            "new_interval": result["interval"],
            "next_review_at": result["next_review_at"],
        },
    }


@router.post("/feynman")
def submit_feynman(req: FeynmanRequest, db: Session = Depends(get_db)):
    """提交费曼解释，返回规则检查反馈"""
    # 获取当前会话的目标节点
    session = db.query(DailySession).filter(
        DailySession.id == req.session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    loader = get_loader()
    target_node = loader.get_node(session.target_node or "")

    if not target_node:
        # 无目标节点时使用默认检查
        return check_feynman(
            req.explanation,
            key_elements=[],
            missing_hints={},
            min_length=config.feynman.get("rule", {}).get("min_text_length", 20),
            min_match_ratio=config.feynman.get("rule", {}).get("min_match_ratio", 0.5),
        )

    feynman_config = target_node.get("feynman", {})
    key_elements = feynman_config.get("key_elements", [])
    missing_hints = feynman_config.get("missing_hints", {})

    return check_feynman(
        req.explanation,
        key_elements=key_elements,
        missing_hints=missing_hints,
        min_length=config.feynman.get("rule", {}).get("min_text_length", 20),
        min_match_ratio=config.feynman.get("rule", {}).get("min_match_ratio", 0.5),
    )


@router.post("/calibrate")
def submit_calibrate(req: CalibrateRequest, db: Session = Depends(get_db)):
    """提交自我校准 + 今日深思"""
    session = db.query(DailySession).filter(
        DailySession.id == req.session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 保存思想日记
    if req.thought_diary.strip():
        diary = ThoughtDiary(
            session_date=session.session_date,
            node_slug=session.target_node,
            prompt="今日深思卡",
            reflection=req.thought_diary,
            created_at=datetime.now().isoformat(),
        )
        db.add(diary)

    # 更新会话步骤状态
    steps = json.loads(session.steps_data or "{}")
    steps["calibration"] = {"confidence": req.confidence}
    session.steps_data = json.dumps(steps, ensure_ascii=False)
    db.commit()

    return {"status": "ok"}


@router.post("/complete")
def complete_session(req: CompleteRequest, db: Session = Depends(get_db)):
    """标记会话完成"""
    session = db.query(DailySession).filter(
        DailySession.id == req.session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session.status = "completed"
    session.completed_at = datetime.now().isoformat()
    session.total_time_sec = req.total_time_sec
    db.commit()

    return {"status": "ok", "session_id": req.session_id}
