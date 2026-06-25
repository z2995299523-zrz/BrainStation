"""AI API —— SSE 流式提问 + 生成练习题"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config import config
from ..content.loader import ContentLoader
from ..database import get_db
from ..services.ai_orchestrator import AIOrchestrator
from ..dependencies import get_current_user
from ..models import User

router = APIRouter(prefix="/api/ai", tags=["ai"])

# 单例
_loader: ContentLoader | None = None
_orchestrator: AIOrchestrator | None = None


def get_orchestrator() -> AIOrchestrator:
    global _loader, _orchestrator
    if _loader is None:
        content_dir = config.app.get("content_dir", "./content")
        _loader = ContentLoader(content_dir)
        _loader.load_all()
    if _orchestrator is None:
        _orchestrator = AIOrchestrator(_loader)
    return _orchestrator


# ── 请求模型 ──

class AskRequest(BaseModel):
    chapter_slug: str
    current_stage: str = "concept"  # concept|examples|practice|test|summary
    current_position: str = ""  # e.g. "例题 2/3"
    question: str
    history: list[dict] = []  # [{role: "user"|"assistant", content: str}, ...]


class GeneratePracticeRequest(BaseModel):
    chapter_slug: str
    difficulty: int = 1
    count: int = 3


# ── 端点 ──

@router.post("/ask")
async def ask(
    req: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    AI 导师提问（SSE 流式返回）

    请求体:
    - chapter_slug: 当前章节
    - current_stage: 当前阶段
    - current_position: 具体位置（如"例题 2/3"）
    - question: 用户的问题

    返回: SSE 流，每段是 AI 回复的文本片段
    """
    orchestrator = get_orchestrator()

    async def event_stream():
        async for chunk in orchestrator.ask(
            db=db,
            user_id=current_user.id,
            chapter_slug=req.chapter_slug,
            current_stage=req.current_stage,
            current_position=req.current_position,
            user_question=req.question,
            history=req.history,
        ):
            # SSE 格式：data: <content>\n\n
            yield f"data: {chunk}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/generate-practice")
async def generate_practice(
    req: GeneratePracticeRequest,
    current_user: User = Depends(get_current_user),
):
    """
    生成额外练习题

    请求体:
    - chapter_slug: 章节 slug
    - difficulty: 难度 1-5
    - count: 生成题数（默认 3）

    返回: { questions: [...] }
    """
    orchestrator = get_orchestrator()
    try:
        result = await orchestrator.generate_extra_practice(
            chapter_slug=req.chapter_slug,
            difficulty=req.difficulty,
            count=req.count,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
