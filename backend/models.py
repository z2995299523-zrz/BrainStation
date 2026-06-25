"""SQLAlchemy ORM 模型"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
    role = Column(String(20), default="learner")  # learner | examiner | admin
    created_at = Column(String)


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    node_slug = Column(String(50), nullable=False)
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
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


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    chapter_slug = Column(String(50), nullable=False)
    title = Column(String(100), default="新对话")
    created_at = Column(String)
    updated_at = Column(String)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(10), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(String)


# ── 考试模块 ──

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    subject = Column(String(10), nullable=False)  # "math" | "english"
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), default="draft")  # draft | published | archived
    chapters = Column(Text, default="[]")  # JSON: ["slug1", "slug2"]
    question_count = Column(Integer, default=10)
    time_limit_min = Column(Integer, default=60)
    difficulty_level = Column(String(10), default="mixed")  # easy | medium | hard | mixed
    passing_score = Column(Integer, default=60)  # 百分比
    created_at = Column(String)
    updated_at = Column(String)


class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, index=True)
    question_index = Column(Integer, nullable=False)  # 排序
    stem = Column(Text, nullable=False)
    options = Column(Text, nullable=True)  # JSON: ["A: xxx", "B: xxx"]
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, default="")
    difficulty = Column(Integer, default=1)  # 1-5
    q_type = Column(String(10), default="choice")  # choice | fill
    chapter_slug = Column(String(50), nullable=True)
    created_at = Column(String)


class ExamAttempt(Base):
    __tablename__ = "exam_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), default="in_progress")  # in_progress | completed
    score = Column(Integer, nullable=True)  # 0-100
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    answers = Column(Text, default="[]")  # JSON: [{question_id, user_answer, is_correct}]
    weak_areas = Column(Text, default="[]")  # JSON: [{chapter_slug, accuracy, error_count}]
    time_spent_sec = Column(Integer, nullable=True)
    started_at = Column(String)
    completed_at = Column(String, nullable=True)


class ExamResult(Base):
    __tablename__ = "exam_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    attempt_id = Column(Integer, ForeignKey("exam_attempts.id"), nullable=False, index=True)
    chapter_slug = Column(String(50), nullable=False)
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    errors_analysis = Column(Text, default="{}")  # JSON
    created_at = Column(String)


class SchemaVersion(Base):
    __tablename__ = "_schema_version"

    version = Column(Integer, primary_key=True)
    applied_at = Column(String)
