"""FastAPI 应用入口"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import config
from .database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时建表 + 加载内容"""
    # 启动
    init_db()
    yield
    # 关闭（暂无清理逻辑）


app = FastAPI(
    title=config.app.get("name", "初中数英思维训练营"),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — 允许前端开发服务器
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 注册路由 ──
from .routers import session, progress, admin

app.include_router(session.router)
app.include_router(progress.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    """健康检查"""
    from .content.loader import ContentLoader
    content_dir = config.app.get("content_dir", "./content")
    loader = ContentLoader(content_dir)
    loader.load_all()
    return {
        "status": "ok",
        "nodes_loaded": len(loader.get_all_nodes()),
        "questions_loaded": sum(
            len(v) for v in loader.get_all_questions().values()
        ),
    }


# ── 生产模式：服务前端静态文件 ──
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """SPA fallback — 非 API 路径返回静态文件或 index.html"""
        # 不拦截 API 请求
        if full_path.startswith("api/"):
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
