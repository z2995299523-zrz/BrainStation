"""SQLAlchemy ORM 模型 —— 5 张表"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_slug = Column(String(50), unique=True, nullable=False)
    status = Column(String(15), default="locked")  # locked|unlocked|learning|mastered|degraded
    mastery_level = Column(Float, default=0.0)
    ef = Column(Float, default=2.5)
    interval_days = Column(Integer, default=0)
    repetitions = Column(Integer, default=0)
    next_review_at = Column(String, nullable=True)
    total_attempts = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    last_study_at = Column(String, nullable=True)
    created_at = Column(String)
    updated_at = Column(String)


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_slug = Column(String(50), nullable=False)
    question_id = Column(String(50), nullable=False)
    session_id = Column(Integer, nullable=True)
    attempt_number = Column(Integer, default=1)
    user_answer = Column(Text, nullable=True)  # JSON string
    is_correct = Column(Boolean, nullable=True)
    quality_score = Column(Integer, default=0)
    confidence = Column(Integer, nullable=True)
    time_spent_sec = Column(Integer, nullable=True)
    created_at = Column(String)


class DailySession(Base):
    __tablename__ = "daily_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_date = Column(String, nullable=False)
    subject = Column(String(10), default="")  # "math" | "english" | ""（未指定）
    day_number = Column(Integer, nullable=False)
    status = Column(String(15), default="in_progress")
    target_node = Column(String(50), nullable=True)
    started_at = Column(String)
    completed_at = Column(String, nullable=True)
    total_time_sec = Column(Integer, nullable=True)
    steps_data = Column(Text, default="{}")  # JSON


class ThoughtDiary(Base):
    __tablename__ = "thought_diaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_date = Column(String, nullable=False)
    node_slug = Column(String(50), nullable=True)
    prompt = Column(Text, nullable=True)
    reflection = Column(Text, nullable=False)
    created_at = Column(String)


class ConfigChange(Base):
    __tablename__ = "config_changelog"

    id = Column(Integer, primary_key=True, autoincrement=True)
    changed_at = Column(String)
    param_path = Column(String(100))
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    note = Column(Text, nullable=True)
