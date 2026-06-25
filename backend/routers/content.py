"""内容 API —— 章节内容读取 + 答题提交"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config import config
from ..content.loader import ContentLoader
from ..database import get_db
from ..engine.chapter_engine import ChapterEngine
from ..models import User
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/content", tags=["content"])

# 内容加载器（单例）
_loader: ContentLoader | None = None
_engine: ChapterEngine | None = None


def get_engine() -> ChapterEngine:
    global _loader, _engine
    if _loader is None:
        content_dir = config.app.get("content_dir", "./content")
        _loader = ContentLoader(content_dir)
        _loader.load_all()
    if _engine is None:
        _engine = ChapterEngine(_loader)
    return _engine


# ── 请求模型 ──

class SubmitAnswerRequest(BaseModel):
    chapter_slug: str
    question_id: str
    user_answer: str
    difficulty: int = 1
    layer: str = "operation"


# ── 端点 ──

@router.get("/chapter")
def get_chapter(
    slug: str = Query(..., description="章节 slug"),
    stage: str = Query("concept", description="阶段: concept|examples|practice|test|summary"),
    current_user: User = Depends(get_current_user),
):
    """
    获取指定章节 + 阶段的学习内容

    - **slug**: 章节标识（如 factorization, rational-numbers）
    - **stage**: 学习阶段
        - concept: 概念讲解
        - examples: 例题展示
        - practice: 练习题
        - test: 综合测试
        - summary: 章节总结
    """
    engine = get_engine()
    try:
        result = engine.get_chapter(slug, stage)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-answer")
def submit_answer(
    req: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    提交一道题的答案

    系统会：
    1. 判断答案正误
    2. 更新 SM-2 间隔重复状态
    3. 记录答题历史
    4. 返回反馈（正误、正确解法、掌握度变化）
    """
    engine = get_engine()
    try:
        result = engine.submit_answer(
            db=db,
            user_id=current_user.id,
            user_answer=req.user_answer,
            question_id=req.question_id,
            chapter_slug=req.chapter_slug,
            difficulty=req.difficulty,
            layer=req.layer,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
