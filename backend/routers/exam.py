"""考试 API —— 考试生成、参加、结果分析"""
import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..config import config
from ..content.loader import ContentLoader
from ..database import get_db
from ..models import User, Exam, ExamQuestion, ExamAttempt, ExamResult
from ..dependencies import get_current_user, require_role
from ..services.ai_orchestrator import AIOrchestrator
from ..services.exam_service import ExamService

router = APIRouter(prefix="/api/exam", tags=["exam"])

# ── 单例 ──

_loader: Optional[ContentLoader] = None
_orchestrator: Optional[AIOrchestrator] = None
_exam_service: Optional[ExamService] = None


def get_loader() -> ContentLoader:
    global _loader
    if _loader is None:
        _loader = ContentLoader(config.app.get("content_dir", "./content"))
        _loader.load_all()
    return _loader


def get_orchestrator() -> AIOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AIOrchestrator(get_loader())
    return _orchestrator


def get_exam_service() -> ExamService:
    global _exam_service
    if _exam_service is None:
        _exam_service = ExamService(get_loader())
    return _exam_service


# ── 请求/响应模型 ──


class GenerateExamRequest(BaseModel):
    subject: str = Field(..., description="学科: math | english")
    chapter_slugs: list[str] = Field(..., min_length=1, description="选中的章节 slug 列表")
    question_count: int = Field(default=15, ge=5, le=50, description="总题数")
    difficulty_level: str = Field(default="mixed", description="easy | medium | hard | mixed")
    title: str = Field(default="", description="考试标题")
    description: str = Field(default="", description="考试描述")
    time_limit_min: int = Field(default=60, ge=10, le=180, description="时间限制（分钟）")
    passing_score: int = Field(default=60, ge=10, le=100, description="及格线（百分比）")


class SubmitAnswerRequest(BaseModel):
    attempt_id: int
    question_id: int
    answer: str


class PublishRequest(BaseModel):
    status: str = "published"


# ── 辅助函数 ──


def _build_difficulty_distribution(level: str, count: int) -> dict[int, int]:
    """根据难度级别计算各难度的题数分布"""
    if level == "easy":
        return {1: count // 2, 2: count - count // 2}
    elif level == "hard":
        return {4: count // 2, 5: count - count // 2}
    elif level == "medium":
        return {3: count}
    else:  # mixed: 正态分布
        return {
            1: max(1, count // 5),
            2: max(1, count // 5),
            3: count // 3,
            4: max(1, count // 5),
            5: max(1, count // 5),
        }


# ── 所有已认证用户可访问 ──


@router.get("/list")
def list_exams(
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """列出已发布的考试"""
    query = db.query(Exam).filter(Exam.status == "published")
    if subject:
        query = query.filter(Exam.subject == subject)
    exams = query.order_by(Exam.updated_at.desc()).all()

    results = []
    for e in exams:
        # 检查用户是否有已完成 attempt
        attempts = (
            db.query(ExamAttempt)
            .filter(
                ExamAttempt.exam_id == e.id,
                ExamAttempt.user_id == current_user.id,
            )
            .order_by(ExamAttempt.completed_at.desc())
            .all()
        )
        last_score = None
        completed_count = 0
        if attempts:
            completed = [a for a in attempts if a.status == "completed"]
            completed_count = len(completed)
            if completed:
                last_score = completed[0].score

        results.append({
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "subject": e.subject,
            "chapters": json.loads(e.chapters or "[]"),
            "question_count": e.question_count,
            "time_limit_min": e.time_limit_min,
            "difficulty_level": e.difficulty_level,
            "passing_score": e.passing_score,
            "created_at": e.created_at,
            "last_score": last_score,
            "attempts_count": completed_count,
        })

    return results


@router.get("/{exam_id}")
def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExamService = Depends(get_exam_service),
):
    """获取考试详情（含题目，不含答案）"""
    try:
        return service.get_exam_with_questions(db, exam_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{exam_id}/start")
def start_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExamService = Depends(get_exam_service),
):
    """开始考试（创建 attempt）"""
    try:
        attempt = service.start_attempt(db, exam_id, current_user.id)
        return {
            "attempt_id": attempt.id,
            "status": attempt.status,
            "total_questions": attempt.total_questions,
            "started_at": attempt.started_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{exam_id}/answer")
def submit_answer(
    exam_id: int,
    req: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExamService = Depends(get_exam_service),
):
    """提交单题答案"""
    try:
        return service.submit_answer(
            db, exam_id, req.attempt_id, req.question_id, req.answer
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{exam_id}/finish")
def finish_exam(
    exam_id: int,
    attempt_id: int = Query(..., description="attempt ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ExamService = Depends(get_exam_service),
):
    """完成考试，计算分数和分析"""
    try:
        return service.finish_attempt(db, exam_id, attempt_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{exam_id}/result/{attempt_id}")
def get_result(
    exam_id: int,
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取考试结果详情"""
    attempt = (
        db.query(ExamAttempt)
        .filter(ExamAttempt.id == attempt_id, ExamAttempt.user_id == current_user.id)
        .first()
    )
    if not attempt:
        raise HTTPException(status_code=404, detail="考试记录不存在")

    answers = json.loads(attempt.answers or "[]")
    weak_areas = json.loads(attempt.weak_areas or "[]")
    exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()

    # 补充每题详情
    detailed_answers = []
    for a in answers:
        q = db.query(ExamQuestion).filter(ExamQuestion.id == a["question_id"]).first()
        options = json.loads(q.options) if q and q.options else None
        detailed_answers.append({
            "question_id": a["question_id"],
            "user_answer": a["user_answer"],
            "is_correct": a["is_correct"],
            "stem": q.stem if q else "",
            "correct_answer": q.correct_answer if q else "",
            "explanation": q.explanation if q else "",
            "options": options,
            "q_type": q.q_type if q else "fill",
            "chapter_slug": q.chapter_slug if q else "",
        })

    return {
        "attempt_id": attempt.id,
        "exam_id": attempt.exam_id,
        "exam_title": exam.title if exam else "",
        "status": attempt.status,
        "score": attempt.score,
        "total_questions": attempt.total_questions,
        "correct_count": attempt.correct_count,
        "passed": (attempt.score or 0) >= (exam.passing_score if exam else 60),
        "passing_score": exam.passing_score if exam else 60,
        "weak_areas": weak_areas,
        "answers": detailed_answers,
        "time_spent_sec": attempt.time_spent_sec,
        "started_at": attempt.started_at,
        "completed_at": attempt.completed_at,
    }


# ── 考核者/管理员专用 ──


require_examiner = require_role("examiner", "admin")


@router.post("/generate")
async def generate_exam(
    req: GenerateExamRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_examiner),
    loader: ContentLoader = Depends(get_loader),
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
    service: ExamService = Depends(get_exam_service),
):
    """AI 生成考试题（考核者/管理员）"""
    # 验证章节存在
    for slug in req.chapter_slugs:
        node = loader.get_node(slug)
        if not node:
            raise HTTPException(status_code=400, detail=f"章节不存在: {slug}")

    # 收集章节数据
    chapters_data = service.collect_chapters_data(req.chapter_slugs)
    if not chapters_data:
        raise HTTPException(status_code=400, detail="没有找到有效的章节数据")

    # 生成标题
    title = req.title or f"{'数学' if req.subject == 'math' else '英语'}综合考试"
    if not req.title:
        chapter_titles = [c["title"] for c in chapters_data[:3]]
        title = f"{title}（{', '.join(chapter_titles)}等）"

    # 创建考试记录
    exam = service.create_exam_record(
        db=db,
        creator_id=current_user.id,
        title=title,
        description=req.description,
        subject=req.subject,
        chapters=req.chapter_slugs,
        question_count=req.question_count,
        time_limit_min=req.time_limit_min,
        difficulty_level=req.difficulty_level,
        passing_score=req.passing_score,
    )

    # AI 生成题目
    difficulty_dist = _build_difficulty_distribution(
        req.difficulty_level, req.question_count
    )

    try:
        questions = await orchestrator.generate_exam(
            chapters_data=chapters_data,
            subject=req.subject,
            question_count=req.question_count,
            difficulty_distribution=difficulty_dist,
        )
    except Exception as e:
        # AI 生成失败，但考试记录已创建（保持 draft）
        return {
            "exam_id": exam.id,
            "status": "draft",
            "error": f"AI 出题失败: {str(e)}",
            "title": title,
        }

    if not questions:
        return {
            "exam_id": exam.id,
            "status": "draft",
            "error": "AI 未能生成有效题目，请重试",
            "title": title,
        }

    # 保存题目
    service.save_exam_questions(db, exam.id, questions)

    # 刷新考试状态
    exam.status = "draft"
    exam.question_count = len(questions)
    exam.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(exam)

    return {
        "exam_id": exam.id,
        "title": exam.title,
        "subject": exam.subject,
        "question_count": exam.question_count,
        "status": exam.status,
        "created_at": exam.created_at,
    }


@router.put("/{exam_id}/publish")
def publish_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_examiner),
):
    """发布考试"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    # 检查是否已有题目
    q_count = (
        db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).count()
    )
    if q_count == 0:
        raise HTTPException(status_code=400, detail="考试没有题目，无法发布")

    exam.status = "published"
    exam.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()

    return {"status": "published", "exam_id": exam_id}


@router.put("/{exam_id}")
def update_exam(
    exam_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    time_limit_min: Optional[int] = None,
    passing_score: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_examiner),
):
    """更新考试元数据"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    if title is not None:
        exam.title = title
    if description is not None:
        exam.description = description
    if time_limit_min is not None:
        exam.time_limit_min = time_limit_min
    if passing_score is not None:
        exam.passing_score = passing_score

    exam.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()

    return {"status": "updated", "exam_id": exam_id}


@router.delete("/{exam_id}")
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_examiner),
):
    """删除考试（级联删除题目、attempts、results）"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    # 级联删除
    db.query(ExamResult).filter(
        ExamResult.attempt_id.in_(
            db.query(ExamAttempt.id).filter(ExamAttempt.exam_id == exam_id)
        )
    ).delete(synchronize_session=False)
    db.query(ExamAttempt).filter(ExamAttempt.exam_id == exam_id).delete(
        synchronize_session=False
    )
    db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).delete(
        synchronize_session=False
    )
    db.delete(exam)
    db.commit()

    return {"status": "deleted", "exam_id": exam_id}


@router.get("/manage/list")
def manage_exams(
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_examiner),
):
    """管理端：列出所有考试（含草稿）"""
    query = db.query(Exam)
    if subject:
        query = query.filter(Exam.subject == subject)
    exams = query.order_by(Exam.updated_at.desc()).all()

    results = []
    for e in exams:
        # 统计参加人数
        attempt_count = (
            db.query(ExamAttempt)
            .filter(ExamAttempt.exam_id == e.id)
            .count()
        )
        results.append({
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "subject": e.subject,
            "status": e.status,
            "chapters": json.loads(e.chapters or "[]"),
            "question_count": e.question_count,
            "time_limit_min": e.time_limit_min,
            "difficulty_level": e.difficulty_level,
            "passing_score": e.passing_score,
            "attempt_count": attempt_count,
            "created_at": e.created_at,
            "updated_at": e.updated_at,
        })

    return results


@router.get("/manage/{exam_id}/results")
def view_exam_results(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_examiner),
):
    """管理端：查看某考试所有用户的成绩"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    attempts = (
        db.query(ExamAttempt)
        .filter(ExamAttempt.exam_id == exam_id, ExamAttempt.status == "completed")
        .order_by(ExamAttempt.completed_at.desc())
        .all()
    )

    results = []
    for a in attempts:
        user = db.query(User).filter(User.id == a.user_id).first()
        results.append({
            "attempt_id": a.id,
            "username": user.username if user else "未知用户",
            "score": a.score,
            "correct_count": a.correct_count,
            "total_questions": a.total_questions,
            "passed": (a.score or 0) >= (exam.passing_score or 60),
            "time_spent_sec": a.time_spent_sec,
            "completed_at": a.completed_at,
        })

    return {
        "exam_id": exam_id,
        "exam_title": exam.title,
        "total_attempts": len(results),
        "avg_score": sum(r["score"] or 0 for r in results) / len(results) if results else 0,
        "passing_score": exam.passing_score,
        "results": results,
    }
