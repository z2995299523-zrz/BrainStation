"""数据库迁移框架 —— 版本化管理 schema 变更，保护已有数据

每个迁移函数接收 db session，通过 ALTER TABLE / CREATE TABLE 安全地修改 schema。
迁移按版本号顺序执行，每步执行前检查是否需要执行（等幂）。

关键原则：
- 永远不 DROP TABLE（除非回滚显式指定）
- 新增列用 ALTER TABLE ADD COLUMN（SQLite 3.25+）
- 新增表用 Base.metadata.create_all() 安全创建
- 已有数据的列始终保留默认值
"""

import re
from datetime import datetime, timezone
from typing import Callable

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

# ── 迁移注册表 ──
# 格式: (version: int, description: str, migrate_fn: Callable[[Session], None])
MIGRATIONS: list[tuple[int, str, Callable[[Session], None]]] = []


def migration(version: int, description: str):
    """装饰器：注册一个迁移函数"""

    def decorator(func: Callable[[Session], None]):
        MIGRATIONS.append((version, description, func))
        return func

    return decorator


def get_current_version(db: Session) -> int:
    """读取当前数据库的 schema 版本号，_schema_version 表不存在则返回 0"""
    inspector = inspect(db.bind)
    if "_schema_version" not in inspector.get_table_names():
        return 0
    result = db.execute(
        text("SELECT COALESCE(MAX(version), 0) FROM _schema_version")
    ).scalar()
    return result or 0


def run_pending_migrations(db: Session) -> int:
    """按版本顺序执行所有待执行的迁移，返回本次执行的迁移数量"""
    current = get_current_version(db)
    applied = 0

    for version, description, func in sorted(MIGRATIONS, key=lambda x: x[0]):
        if version > current:
            print(f"[Migrate] v{version}: {description} ...")
            func(db)
            db.execute(
                text(
                    "INSERT INTO _schema_version (version, applied_at) "
                    "VALUES (:v, :t)"
                ),
                {"v": version, "t": datetime.now(timezone.utc).isoformat()},
            )
            db.commit()
            print(f"[Migrate] v{version} applied.")
            applied += 1

    if applied == 0:
        print(f"[Migrate] 数据库已是最新 (v{current})")
    return applied


# ═══════════════════════════════════════════════════════════════════
# 迁移定义
# ═══════════════════════════════════════════════════════════════════


@migration(1, "添加 role 列到 users 表")
def migrate_v1_add_role(db: Session) -> None:
    """为已有用户设置默认角色 learner，新用户注册时也默认为 learner"""
    inspector = inspect(db.bind)
    columns = [c["name"] for c in inspector.get_columns("users")]
    if "role" not in columns:
        db.execute(
            text(
                "ALTER TABLE users ADD COLUMN role VARCHAR(20) "
                "NOT NULL DEFAULT 'learner'"
            )
        )
        print("  + users.role 列已添加")
    else:
        print("  - users.role 列已存在，跳过")


@migration(2, "创建考试和 schema_version 表")
def migrate_v2_exam_tables(db: Session) -> None:
    """创建 exams / exam_questions / exam_attempts / exam_results 表"""
    from .models import Base

    inspector = inspect(db.bind)
    existing = inspector.get_table_names()
    created = []

    # 只创建还不存在的表（Base.metadata.create_all 对待存在的表是 no-op，
    # 但用 checkfirst 更精确）
    target_tables = {"exams", "exam_questions", "exam_attempts", "exam_results"}
    if target_tables.issubset(existing):
        print("  - 考试相关表已存在，跳过")
        return

    # 用原始 SQL 创建（避免 create_all 触及其他表的副作用）
    tables_sql = [
        # exams
        """CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            description TEXT DEFAULT '',
            subject VARCHAR(10) NOT NULL,
            creator_id INTEGER NOT NULL REFERENCES users(id),
            status VARCHAR(20) DEFAULT 'draft',
            chapters TEXT DEFAULT '[]',
            question_count INTEGER DEFAULT 10,
            time_limit_min INTEGER DEFAULT 60,
            difficulty_level VARCHAR(10) DEFAULT 'mixed',
            passing_score INTEGER DEFAULT 60,
            created_at VARCHAR,
            updated_at VARCHAR
        )""",
        # exam_questions
        """CREATE TABLE IF NOT EXISTS exam_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL REFERENCES exams(id),
            question_index INTEGER NOT NULL,
            stem TEXT NOT NULL,
            options TEXT,
            correct_answer TEXT NOT NULL,
            explanation TEXT DEFAULT '',
            difficulty INTEGER DEFAULT 1,
            q_type VARCHAR(10) DEFAULT 'choice',
            chapter_slug VARCHAR(50),
            created_at VARCHAR
        )""",
        # exam_attempts
        """CREATE TABLE IF NOT EXISTS exam_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL REFERENCES exams(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            status VARCHAR(20) DEFAULT 'in_progress',
            score INTEGER,
            total_questions INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            answers TEXT DEFAULT '[]',
            weak_areas TEXT DEFAULT '[]',
            time_spent_sec INTEGER,
            started_at VARCHAR,
            completed_at VARCHAR
        )""",
        # exam_results
        """CREATE TABLE IF NOT EXISTS exam_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id INTEGER NOT NULL REFERENCES exam_attempts(id),
            chapter_slug VARCHAR(50) NOT NULL,
            total_questions INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            accuracy FLOAT DEFAULT 0.0,
            errors_analysis TEXT DEFAULT '{}',
            created_at VARCHAR
        )""",
        # exam_attempts index
        """CREATE INDEX IF NOT EXISTS idx_exam_attempts_exam_id ON exam_attempts(exam_id)""",
        """CREATE INDEX IF NOT EXISTS idx_exam_attempts_user_id ON exam_attempts(user_id)""",
        # exam_questions index
        """CREATE INDEX IF NOT EXISTS idx_exam_questions_exam_id ON exam_questions(exam_id)""",
    ]

    for sql in tables_sql:
        try:
            db.execute(text(sql))
            # 从 SQL 中提取表名用于日志
            match = re.search(r"CREATE TABLE IF NOT EXISTS (\w+)", sql)
            if match:
                table_name = match.group(1)
                if table_name not in existing:
                    created.append(table_name)
        except Exception as e:
            print(f"  ! 执行 SQL 出错: {e}")
            print(f"    SQL: {sql[:80]}...")

    if created:
        print(f"  + 已创建表: {', '.join(created)}")
    else:
        print("  - 考试相关表已存在，跳过")

    db.commit()
