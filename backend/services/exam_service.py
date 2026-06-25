"""考试服务 —— 考试生成、答题评估、短板分析"""
import json
from datetime import datetime, timezone
from collections import defaultdict

from sqlalchemy.orm import Session

from ..content.loader import ContentLoader
from ..models import Exam, ExamQuestion, ExamAttempt, ExamResult


class ExamService:
    """考试业务逻辑"""

    def __init__(self, loader: ContentLoader):
        self.loader = loader

    # ── 考试生成 ──────────────────────────────────────────────

    def collect_chapters_data(self, chapter_slugs: list[str]) -> list[dict]:
        """收集多个章节的教学数据用于 AI 出题"""
        chapters = []
        for slug in chapter_slugs:
            node = self.loader.get_node(slug)
            if node:
                chapters.append({
                    "slug": slug,
                    "title": node.get("title", slug),
                    "ai_context": node.get("ai_context", {}),
                })
        return chapters

    def create_exam_record(
        self,
        db: Session,
        creator_id: int,
        title: str,
        description: str,
        subject: str,
        chapters: list[str],
        question_count: int,
        time_limit_min: int,
        difficulty_level: str,
        passing_score: int,
    ) -> Exam:
        """创建考试记录（不含题目）"""
        now = datetime.now(timezone.utc).isoformat()
        exam = Exam(
            title=title,
            description=description,
            subject=subject,
            creator_id=creator_id,
            status="draft",
            chapters=json.dumps(chapters, ensure_ascii=False),
            question_count=question_count,
            time_limit_min=time_limit_min,
            difficulty_level=difficulty_level,
            passing_score=passing_score,
            created_at=now,
            updated_at=now,
        )
        db.add(exam)
        db.commit()
        db.refresh(exam)
        return exam

    def save_exam_questions(
        self,
        db: Session,
        exam_id: int,
        questions: list[dict],
    ) -> list[ExamQuestion]:
        """批量保存考试题目"""
        now = datetime.now(timezone.utc).isoformat()
        question_objs = []
        for i, q in enumerate(questions):
            options = q.get("options")
            eq = ExamQuestion(
                exam_id=exam_id,
                question_index=q.get("question_index", i + 1),
                stem=q.get("stem", ""),
                options=json.dumps(options, ensure_ascii=False) if options else None,
                correct_answer=str(q.get("correct_answer", "")),
                explanation=q.get("explanation", ""),
                difficulty=int(q.get("difficulty", 1)),
                q_type=q.get("q_type", "fill"),
                chapter_slug=q.get("chapter_slug", ""),
                created_at=now,
            )
            db.add(eq)
            question_objs.append(eq)

        # 更新 exam 的 question_count
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if exam:
            exam.question_count = len(questions)
            exam.updated_at = now

        db.commit()
        return question_objs

    # ── 答题 ──────────────────────────────────────────────────

    def get_exam_with_questions(self, db: Session, exam_id: int) -> dict:
        """获取考试详情（含题目列表，不含答案）"""
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise ValueError(f"考试不存在: {exam_id}")

        questions = (
            db.query(ExamQuestion)
            .filter(ExamQuestion.exam_id == exam_id)
            .order_by(ExamQuestion.question_index)
            .all()
        )

        return {
            "id": exam.id,
            "title": exam.title,
            "description": exam.description,
            "subject": exam.subject,
            "status": exam.status,
            "chapters": json.loads(exam.chapters or "[]"),
            "question_count": exam.question_count,
            "time_limit_min": exam.time_limit_min,
            "difficulty_level": exam.difficulty_level,
            "passing_score": exam.passing_score,
            "questions": [
                {
                    "id": q.id,
                    "question_index": q.question_index,
                    "stem": q.stem,
                    "options": json.loads(q.options) if q.options else None,
                    "difficulty": q.difficulty,
                    "q_type": q.q_type,
                    "chapter_slug": q.chapter_slug,
                }
                for q in questions
            ],
        }

    def start_attempt(
        self, db: Session, exam_id: int, user_id: int
    ) -> ExamAttempt:
        """开始考试：创建 attempt 记录"""
        # 检查是否有未完成的 attempt
        existing = (
            db.query(ExamAttempt)
            .filter(
                ExamAttempt.exam_id == exam_id,
                ExamAttempt.user_id == user_id,
                ExamAttempt.status == "in_progress",
            )
            .first()
        )
        if existing:
            return existing

        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise ValueError(f"考试不存在: {exam_id}")
        if exam.status != "published":
            raise ValueError("考试尚未发布，无法参加")

        now = datetime.now(timezone.utc).isoformat()
        attempt = ExamAttempt(
            exam_id=exam_id,
            user_id=user_id,
            status="in_progress",
            total_questions=exam.question_count,
            started_at=now,
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt

    def submit_answer(
        self,
        db: Session,
        exam_id: int,
        attempt_id: int,
        question_id: int,
        user_answer: str,
    ) -> dict:
        """提交单题答案，返回正误判断"""
        question = (
            db.query(ExamQuestion)
            .filter(ExamQuestion.id == question_id)
            .first()
        )
        if not question:
            raise ValueError(f"题目不存在: {question_id}")

        # 判断正误（复用和 chapter_engine 一致的逻辑）
        is_correct = check_answer(user_answer, question.correct_answer)

        # 记录到 attempt
        attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
        if not attempt:
            raise ValueError(f"考试记录不存在: {attempt_id}")

        answers = json.loads(attempt.answers or "[]")
        # 如果已答过此题，则更新
        updated = False
        for a in answers:
            if a.get("question_id") == question_id:
                a["user_answer"] = user_answer
                a["is_correct"] = is_correct
                updated = True
                break
        if not updated:
            answers.append({
                "question_id": question_id,
                "user_answer": user_answer,
                "is_correct": is_correct,
            })

        attempt.answers = json.dumps(answers, ensure_ascii=False)
        db.commit()

        return {
            "is_correct": is_correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
        }

    def finish_attempt(
        self, db: Session, exam_id: int, attempt_id: int
    ) -> dict:
        """完成考试：计算分数、分析短板"""
        attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
        if not attempt:
            raise ValueError(f"考试记录不存在: {attempt_id}")
        if attempt.status == "completed":
            # 返回已有结果
            return self._build_result(db, attempt)

        answers = json.loads(attempt.answers or "[]")
        total = len(answers)
        correct = sum(1 for a in answers if a.get("is_correct"))

        # 按章节分析
        chapter_stats = defaultdict(lambda: {"total": 0, "correct": 0})
        for a in answers:
            q = (
                db.query(ExamQuestion)
                .filter(ExamQuestion.id == a["question_id"])
                .first()
            )
            slug = q.chapter_slug if q else "unknown"
            chapter_stats[slug]["total"] += 1
            if a.get("is_correct"):
                chapter_stats[slug]["correct"] += 1

        weak_areas = []
        for slug, stats in chapter_stats.items():
            accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            if accuracy < 0.8:  # 低于 80% 视为薄弱
                # 获取章节标题
                node = self.loader.get_node(slug)
                title = node.get("title", slug) if node else slug
                weak_areas.append({
                    "chapter_slug": slug,
                    "chapter_title": title,
                    "error_count": stats["total"] - stats["correct"],
                    "total_count": stats["total"],
                    "accuracy": round(accuracy, 2),
                })

        # 按准确率排序（最差的在前）
        weak_areas.sort(key=lambda x: x["accuracy"])

        score = round(correct / total * 100) if total > 0 else 0
        now = datetime.now(timezone.utc).isoformat()

        attempt.status = "completed"
        attempt.score = score
        attempt.correct_count = correct
        attempt.total_questions = total
        attempt.weak_areas = json.dumps(weak_areas, ensure_ascii=False)
        attempt.completed_at = now

        # 保存章节结果明细
        for slug, stats in chapter_stats.items():
            accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            result = ExamResult(
                attempt_id=attempt_id,
                chapter_slug=slug,
                total_questions=stats["total"],
                correct_count=stats["correct"],
                accuracy=round(accuracy, 2),
                errors_analysis=json.dumps(
                    self._analyze_chapter_errors(db, attempt_id, slug),
                    ensure_ascii=False,
                ),
                created_at=now,
            )
            db.add(result)

        db.commit()

        return self._build_result(db, attempt)

    def _build_result(self, db: Session, attempt: ExamAttempt) -> dict:
        """构建完整的结果数据"""
        exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
        answers = json.loads(attempt.answers or "[]")
        weak_areas = json.loads(attempt.weak_areas or "[]")

        # 补充每题的详细信息
        detailed_answers = []
        for a in answers:
            q = (
                db.query(ExamQuestion)
                .filter(ExamQuestion.id == a["question_id"])
                .first()
            )
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

    def _analyze_chapter_errors(
        self, db: Session, attempt_id: int, chapter_slug: str
    ) -> dict:
        """分析某个章节的错误模式"""
        attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
        if not attempt:
            return {}
        answers = json.loads(attempt.answers or "[]")
        errors = []
        for a in answers:
            if not a.get("is_correct"):
                q = (
                    db.query(ExamQuestion)
                    .filter(
                        ExamQuestion.id == a["question_id"],
                        ExamQuestion.chapter_slug == chapter_slug,
                    )
                    .first()
                )
                if q:
                    errors.append({
                        "question_id": q.id,
                        "user_answer": a["user_answer"],
                        "correct_answer": q.correct_answer,
                        "stem": q.stem[:100],
                    })

        return {
            "total_errors": len(errors),
            "errors": errors,
        }


# ── 答案匹配（从 chapter_engine 提取的共享逻辑）──────────────────

import re


def check_answer(user_answer: str, correct_answer: str) -> bool:
    """判断用户答案是否正确

    支持 8 层渐进匹配：
    1. 精确匹配
    1.5 数值匹配（忽略单位）
    2. 忽略空格和标点
    3. 前缀匹配（用户只写了开头）
    4. 判断词匹配（是/否 等）
    5. 子串包含
    6. 选择题单字母匹配（大小写不敏感）
    7. 首字母匹配
    8. 模糊匹配（相似度）
    """
    if not user_answer or not correct_answer:
        return False

    ua = str(user_answer).strip()
    ca = str(correct_answer).strip()

    # 1. 精确匹配
    if ua == ca:
        return True

    # 1.5 数值匹配：忽略单位的纯数字比较（"8" vs "8°C"）
    ua_num = re.match(r'^-?\d+(\.\d+)?', ua)
    ca_num = re.match(r'^-?\d+(\.\d+)?', ca)
    if ua_num and ca_num and ua_num.group() == ca_num.group():
        return True

    # 2. 忽略空格和标点符号
    import re as re_mod
    ua_clean = re_mod.sub(r'\s+', '', ua).lower()
    ca_clean = re_mod.sub(r'\s+', '', ca).lower()
    if ua_clean == ca_clean:
        return True

    # 3. 前缀匹配（用户可能只写了开头）
    if len(ua) >= 3 and ca_clean.startswith(ua_clean):
        return True

    # 4. 判断词匹配
    positive = {"是", "对", "正确", "yes", "true", "t", "y"}
    negative = {"否", "错", "错误", "no", "false", "f", "n"}
    ua_lower = ua.lower()
    if ua_lower in positive and ca.lower() in positive:
        return True
    if ua_lower in negative and ca.lower() in negative:
        return True

    # 5. 子串包含
    if len(ua) >= 2 and ua_clean in ca_clean:
        return True
    if len(ua) >= 2 and ca_clean in ua_clean:
        return True

    # 6. 选择题单字母匹配
    if len(ua) == 1 and ua.isalpha() and ua.upper() == ca.upper():
        return True

    # 7. 首字母匹配
    if len(ua) == 1 and ua.isalpha() and len(ca) >= 1 and ua.upper() == ca[0].upper():
        return True

    # 8. 模糊匹配（简单相似度）
    if _similarity(ua_clean, ca_clean) > 0.85:
        return True

    return False


def _similarity(a: str, b: str) -> float:
    """简单的 Jaccard 相似度"""
    if not a or not b:
        return 0.0
    set_a = set(a)
    set_b = set(b)
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0
