"""SQLite 数据库初始化 + 会话管理"""
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from .config import config

DATABASE_URL = f"sqlite:///{config.app.get('database_path', 'data/training.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """初始化数据库：创建基础表 + 执行待迁移脚本

    不会删除已有数据。新增表通过 create_all 安全创建（已存在则跳过），
    新增列和 schema 变更通过 migrate.py 的版本化迁移执行。
    """
    from .models import Base

    # 1. 创建所有还不存在的表（安全操作，已存在的表不受影响）
    Base.metadata.create_all(bind=engine)

    # 2. 执行版本化迁移（ALTER TABLE 等 create_all 做不到的操作）
    from .migrate import run_pending_migrations

    db = SessionLocal()
    try:
        applied = run_pending_migrations(db)
    finally:
        db.close()

    table_count = len(inspect(engine).get_table_names())
    print(f"[DB] 数据库就绪（{table_count} 张表）")


def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
