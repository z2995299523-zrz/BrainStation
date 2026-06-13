"""SQLite 数据库初始化 + 会话管理"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import config

DATABASE_URL = f"sqlite:///{config.app.get('database_path', 'data/training.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """创建所有表（应用启动时调用）"""
    from .models import Base  # noqa: F811
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
