"""章节引擎 —— 按章节+阶段加载内容，驱动 SM-2 间隔重复"""
import json
from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from ..config import config
from ..content.loader import ContentLoader
from ..models import QuestionAttempt, UserProgress
from .sm2 import sm2_update, calculate_mastery


class ChapterEngine:
    """按章节 slug + 阶段 stage 提供学习内容"""

    def __init__(self, loader: ContentLoader):
        self.loader = loader

    # ── 内容读取 ──────────────────────────────────────────────

    def get_chapter(self, slug: str, stage: str) -> dict[str, Any]:
        """
        返回指定章节 + 阶段的学习内容

        stage: concept | examples | practice | test | summary

        返回格式:
        {
            "slug": str,
            "title": str,
            "subject": str,
            "stage": str,
            "data": {...},    # 对应阶段的 display 内容
        }
        """
        node = self.loader.get_node(slug)
        if not node:
            raise ValueError(f"章节不存在: {slug}")

        display = node.get("display", {})
        stage_data = display.get(stage)

        if stage_data is None:
            # 兼容旧格式：从 content 字段中提取
            content = node.get("content", {})
            if stage == "concept":
                # 聚合所有层的内容
                sections = []
                for layer in ("operation", "understand", "connect"):
                    layer_data = content.get(layer, {})
                    text = layer_data.get("text", "")
                    if text:
                        sections.append({"title": layer, "content": text})
                stage_data = {
                    "summary": node.get("title", ""),
                    "sections": sections,
                }
            elif stage in ("practice", "test"):
                # 从 questions 目录加载（旧格式）
                questions = self.loader.get_questions(slug)
                stage_data = questions if questions else []
            else:
                stage_data = {}

        # summary 阶段：从 UserProgress 动态计算
        if stage == "summary":
            stage_data = self._build_summary(node)

        return {
            "slug": slug,
            "title": node.get("title", slug),
            "subject": node.get("subject", ""),
            "stage": stage,
            "data": stage_data,
        }

    def _build_summary(self, node: dict) -> dict:
        """构建总结阶段数据（本章掌握度、关键点、错题回顾）"""
        slug = node.get("slug", "")
        display = node.get("display", {})
        concept = display.get("concept", {})
        return {
            "chapter_title": node.get("title", slug),
            "key_points": [
                s.get("title", "") for s in concept.get("sections", [])
            ],
            "message": "恭喜完成本章学习！回顾上面的关键知识点，确保你已经掌握。",
        }

    # ── 答题 & SM-2 更新 ──────────────────────────────────────

    def submit_answer(
        self,
        db: Session,
        user_id: int,
        user_answer: str,
        question_id: str,
        chapter_slug: str,
        difficulty: int = 1,
        layer: str = "operation",
    ) -> dict[str, Any]:
        """
        提交一道题的答案，判断正误、更新 SM-2 状态、记录答题历史

        返回:
        {
            "is_correct": bool,
            "correct_answer": str,
            "explanation": str,
            "mastery_update": {...},
            "hints": [...],
        }
        """
        # 1. 查找题目
        question = self._find_question(chapter_slug, question_id)

        # 2. 判断正误
        is_correct = False
        correct_answer = ""
        hints = []

        if question:
            correct_answer = str(question.get("answer", ""))
            hints = question.get("hints", [])
            is_correct = self._check_answer(user_answer, correct_answer)
        else:
            # 题目不在题库中（可能是 AI 生成的），默认判定为需要人工检查
            correct_answer = "（需人工判断）"
            is_correct = None

        # 3. 计算 quality（SM-2 输入）
        if is_correct is True:
            quality = 4 if difficulty <= 2 else 3  # 简单题正确=4，难题正确=3
        elif is_correct is False:
            quality = 1
        else:
            quality = 3  # 无法自动判断

        # 4. 查找/创建 UserProgress
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.node_slug == chapter_slug,
        ).first()

        mastery_before = progress.mastery_level if progress else 0.0
        sm2_result = None

        if progress:
            sm2_result = sm2_update(
                quality=quality,
                ef=progress.ef,
                interval=progress.interval_days,
                repetitions=progress.repetitions,
                skip_weekends=config.sm2.get("skip_weekends", True),
            )
            progress.ef = sm2_result["ef"]
            progress.interval_days = sm2_result["interval"]
            progress.repetitions = sm2_result["repetitions"]
            progress.next_review_at = sm2_result["next_review_at"]
            progress.total_attempts += 1
            if is_correct:
                progress.correct_count += 1
            progress.last_study_at = date.today().isoformat()
            progress.updated_at = date.today().isoformat()

            # 重新计算掌握度
            new_mastery = calculate_mastery(
                progress.ef,
                progress.repetitions,
                progress.interval_days,
                progress.last_study_at,
                config.sm2.get("mastery_threshold", 0.85),
            )
            progress.mastery_level = new_mastery

            if new_mastery >= config.sm2.get("mastery_threshold", 0.85):
                progress.status = "mastered"
            elif progress.status in ("locked", "unlocked", "mastered"):
                progress.status = "learning"
        else:
            # 首次学习该章节
            sm2_result = sm2_update(
                quality=quality,
                skip_weekends=config.sm2.get("skip_weekends", True),
            )
            progress = UserProgress(
                user_id=user_id,
                node_slug=chapter_slug,
                status="learning",
                mastery_level=0.0,
                ef=sm2_result["ef"],
                interval_days=sm2_result["interval"],
                repetitions=sm2_result["repetitions"],
                next_review_at=sm2_result["next_review_at"],
                total_attempts=1,
                correct_count=1 if is_correct else 0,
                last_study_at=date.today().isoformat(),
                created_at=date.today().isoformat(),
                updated_at=date.today().isoformat(),
            )
            db.add(progress)

        # 5. 记录答题
        attempt = QuestionAttempt(
            user_id=user_id,
            node_slug=chapter_slug,
            question_id=question_id,
            user_answer=json.dumps(user_answer, ensure_ascii=False),
            is_correct=is_correct,
            quality_score=quality,
            created_at=datetime.now().isoformat(),
        )
        db.add(attempt)
        db.commit()

        # 6. 获取更新后的掌握度
        progress_after = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.node_slug == chapter_slug,
        ).first()
        mastery_after = progress_after.mastery_level if progress_after else 0.0

        # 7. 自动生成讲解（如果 YAML 中没有提供）
        explanation = question.get("explanation", "") if question else ""
        if not explanation and correct_answer:
            explanation = self._auto_explain(correct_answer, question or {})

        return {
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "explanation": explanation,
            "hints": hints if not is_correct else [],
            "mastery_update": {
                "node_slug": chapter_slug,
                "mastery_before": round(mastery_before, 3),
                "mastery_after": round(mastery_after, 3),
                "new_ef": sm2_result["ef"] if sm2_result else config.sm2.get("initial_ef", 2.5),
                "new_interval": sm2_result["interval"] if sm2_result else 0,
                "next_review_at": sm2_result["next_review_at"] if sm2_result else None,
            },
        }

    # ── 内部方法 ──────────────────────────────────────────────

    def _find_question(self, chapter_slug: str, question_id: str) -> dict | None:
        """在 YAML 内容中查找指定题目（先查 display.practice/test，再查 questions 目录）"""
        node = self.loader.get_node(chapter_slug)
        if not node:
            return None

        # 1. 从 display.practice 和 display.test 中查找
        display = node.get("display", {})
        for stage in ("practice", "test"):
            questions = display.get(stage, [])
            if isinstance(questions, list):
                for q in questions:
                    if q.get("id") == question_id:
                        return q

        # 2. 从旧格式 questions 目录查找
        qs = self.loader.get_questions(chapter_slug)
        for q in qs:
            if q.get("id") == question_id:
                return q

        return None

    def _check_answer(self, user_answer: str, correct_answer: str) -> bool:
        """判断用户答案是否正确（支持部分匹配和语义判断）"""
        if not user_answer or not correct_answer:
            return False

        # 规范化
        ua = user_answer.strip().replace(" ", "").replace("（", "(").replace("）", ")")
        ca = correct_answer.strip().replace(" ", "").replace("（", "(").replace("）", ")")

        # 1. 精确匹配（最简单的情况）
        if ua == ca:
            return True

        # 1.5 数值匹配：忽略单位的纯数字比较（"8" vs "8°C", "-3" vs "-3m/s"）
        #      提取双方开头的数值部分，如果一致则接受
        import re
        ua_num = re.match(r'^-?\d+(\.\d+)?', ua)
        ca_num = re.match(r'^-?\d+(\.\d+)?', ca)
        if ua_num and ca_num and ua_num.group() == ca_num.group():
            return True

        # 2. 用户答案作为正确答案的前缀（处理"不是" vs "不是，因为..."）
        #    要求用户答案至少 2 个字符，避免"不"匹配"不是"
        if len(ua) >= 2 and ca.startswith(ua):
            # 确保不是部分匹配导致的错误（如"是"不应匹配"不是"）
            # 如果用户答案只有一个词且是判断词，让它作为精确前缀匹配
            return True

        # 3. 判断词特判：用户只回答了"是"/"不是"/"对"/"错"等
        #    提取正确答案开头的判断词（以标点或空格分隔的第一个词）
        judgement_words = {"是", "不是", "否", "对", "错", "不对", "正确", "错误", "可以", "不能", "有", "没有"}
        ca_first = ca.split("，")[0].split(",")[0].split("。")[0].split(".")[0].split("；")[0].strip()
        if ua in judgement_words and ua == ca_first:
            return True

        # 4. 数学答案：允许用户答案包含在正确答案中（处理多步答案的部分回答）
        #    用户给出了核心答案但没写完整解释
        if len(ua) >= 3 and ua in ca:
            # 再检查是否是判断词的误判：如果 ua 是"是"且 ca 包含"不是"，不应匹配
            if ua == "是" and ca.startswith("不是"):
                return False
            return True

        # 5. 正确答案包含在用户答案中（用户写了解释+答案）
        if len(ca) >= 3 and ca in ua:
            return True

        # 6. 选择题选项匹配：用户回答单个字母（A/B/C/D，大小写不敏感）
        if len(ua) == 1 and ua.isalpha() and ua.upper() == ca.upper():
            return True

        # 7. 用户答案以标点分隔后取首段匹配（处理"d" vs "D"且ca有额外内容的情况）
        if len(ua) == 1 and ua.isalpha() and len(ca) >= 1 and ua.upper() == ca[0].upper():
            return True

        return False

    def _auto_explain(self, correct_answer: str, question: dict) -> str:
        """当 YAML 中没有 explanation 时，自动生成基础讲解"""
        ca = correct_answer.strip()

        # 检测选择题答案（单字母 A-F）
        if len(ca) == 1 and ca.isalpha() and ca.upper() in "ABCDEF":
            stem = question.get("stem", "")
            option_text = self._extract_option_text(stem, ca.upper())
            if option_text:
                return f"正确答案是选项 **{ca.upper()}**：{option_text}"
            return f"正确答案是选项 **{ca.upper()}**"

        # 判断类答案
        if ca in ("是", "不是", "否", "对", "错", "不对", "正确", "错误", "可以", "不能", "有", "没有"):
            return f"正确答案是：**{ca}**"

        # 一般答案
        return f"正确答案是：**{ca}**"

    def _extract_option_text(self, stem: str, option_letter: str) -> str:
        """从选择题题干中提取指定选项的文字内容"""
        import re
        pattern = rf'{option_letter}[：:\.\、\)）]\s*(.+?)(?=\s*[A-F][：:\.\、\)）]|\s*$)'
        match = re.search(pattern, stem)
        if match:
            return match.group(1).strip()
        return ""
