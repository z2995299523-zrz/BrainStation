"""AI 导师编排器 —— 上下文组装 + DeepSeek 流式调用"""
import json
import os
from datetime import date
from typing import AsyncGenerator

from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from ..config import config
from ..content.loader import ContentLoader
from ..models import QuestionAttempt, UserProgress


class AIOrchestrator:
    """AI 导师编排器：组装上下文 → 调用 LLM → 流式返回"""

    def __init__(self, loader: ContentLoader):
        self.loader = loader
        self.client = self._init_client()

    def _init_client(self) -> AsyncOpenAI:
        """初始化 DeepSeek 客户端（config.yaml 优先，环境变量兜底）"""
        deepseek_cfg = config.deepseek
        api_key = deepseek_cfg.get("api_key", "") or os.getenv("DEEPSEEK_API_KEY", "")
        base_url = deepseek_cfg.get("base_url", "") or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        return AsyncOpenAI(api_key=api_key, base_url=base_url)

    # ── 上下文组装 ────────────────────────────────────────────

    def build_context(
        self,
        db: Session,
        user_id: int,
        chapter_slug: str,
        stage: str,
        position: str = "",
    ) -> dict:
        """
        组装注入 LLM 的上下文数据

        参数:
            db: 数据库会话
            chapter_slug: 章节 slug
            stage: 当前阶段 (concept|examples|practice|test|summary)
            position: 具体位置（如 "例题 2/3" 或 "练习第 4 题"）

        返回:
        {
            "chapter": {...},
            "ai_context": {...},    # YAML 中的 ai_context 教案
            "user_progress": {...},
            "recent_errors": [...],
            "prerequisite_status": {...},
        }
        """
        node = self.loader.get_node(chapter_slug)
        if not node:
            raise ValueError(f"章节不存在: {chapter_slug}")

        # 1. 章节基本信息
        chapter_info = {
            "title": node.get("title", chapter_slug),
            "slug": chapter_slug,
            "subject": node.get("subject", ""),
            "current_stage": stage,
            "current_position": position,
        }

        # 2. AI 教案（YAML 中的 ai_context）
        ai_ctx = node.get("ai_context", {})

        # 3. 用户进度
        progress = (
            db.query(UserProgress)
            .filter(UserProgress.user_id == user_id, UserProgress.node_slug == chapter_slug)
            .first()
        )
        user_progress = {
            "mastery": progress.mastery_level if progress else 0.0,
            "status": progress.status if progress else "locked",
            "practice_accuracy": self._calc_accuracy(db, chapter_slug),
            "test_accuracy": self._calc_accuracy(db, chapter_slug),
        }

        # 4. 最近的错题（最多 5 道）
        recent_errors = (
            db.query(QuestionAttempt)
            .filter(
                QuestionAttempt.user_id == user_id,
                QuestionAttempt.node_slug == chapter_slug,
                QuestionAttempt.is_correct == False,  # noqa: E712
            )
            .order_by(QuestionAttempt.created_at.desc())
            .limit(5)
            .all()
        )
        errors_data = [
            {
                "question_id": e.question_id,
                "user_answer": e.user_answer,
            }
            for e in recent_errors
        ]

        # 5. 前置知识掌握状态
        prerequisites = node.get("prerequisites", [])
        prereq_status = {}
        for p_slug in prerequisites:
            p = (
                db.query(UserProgress)
                .filter(UserProgress.user_id == user_id, UserProgress.node_slug == p_slug)
                .first()
            )
            prereq_status[p_slug] = {
                "mastery": p.mastery_level if p else 0.0,
                "status": p.status if p else "locked",
            }

        return {
            "chapter": chapter_info,
            "ai_context": ai_ctx,
            "user_progress": user_progress,
            "recent_errors": errors_data,
            "prerequisite_status": prereq_status,
        }

    # ── 流式提问 ──────────────────────────────────────────────

    async def ask(
        self,
        db: Session,
        user_id: int,
        chapter_slug: str,
        current_stage: str,
        current_position: str,
        user_question: str,
        history: list[dict] | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        用户提问 → SSE 流式返回 AI 回复

        1. 组装上下文
        2. 构建 system prompt
        3. 调用 DeepSeek 流式接口
        4. 逐 chunk yield
        """
        context = self.build_context(db, user_id, chapter_slug, current_stage, current_position)
        system_prompt = self._build_system_prompt(context)

        messages = [{"role": "system", "content": system_prompt}]
        # 拼接对话历史（最近 20 轮，避免 token 爆炸）
        for h in (history or [])[-40:]:
            role = h.get("role", "user")
            content = h.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_question})

        try:
            stream = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=2000,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            yield f"\n\n[AI 服务暂时不可用，请稍后重试。错误信息：{str(e)}]"

    # ── 生成额外练习题 ────────────────────────────────────────

    async def generate_extra_practice(
        self,
        chapter_slug: str,
        difficulty: int,
        count: int = 3,
    ) -> dict:
        """
        按需生成额外练习题

        参数:
            chapter_slug: 章节 slug
            difficulty: 难度 1-5
            count: 生成题数

        返回:
        {
            "questions": [
                {"stem": str, "answer": str, "hints": [str], "difficulty": int},
                ...
            ]
        }
        """
        node = self.loader.get_node(chapter_slug)
        if not node:
            raise ValueError(f"章节不存在: {chapter_slug}")

        ai_ctx = node.get("ai_context", {})
        templates = ai_ctx.get("question_templates", {})
        difficulty_key = f"difficulty_{difficulty}"
        template_hint = templates.get(difficulty_key, "")

        chapter_title = node.get("title", chapter_slug)

        system_prompt = f"""你是一位初中数学和英语老师。请根据以下要求生成练习题。

【章节】{chapter_title}
【难度】{difficulty}/5
【数量】{count} 道
【出题约束】{template_hint if template_hint else "请根据章节内容出题，难度适中"}

请以 JSON 数组格式返回，每道题包含：
- stem: 题目描述
- answer: 正确答案
- hints: 提示列表（2-3个）
- difficulty: 难度数字

只返回 JSON，不要其他文字。"""

        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.8,
                max_tokens=3000,
            )
            content = response.choices[0].message.content or "[]"
            # 尝试提取 JSON
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            questions = json.loads(content)
            return {"questions": questions}
        except json.JSONDecodeError:
            return {"questions": [], "error": "AI 生成的内容格式有误，请重试"}
        except Exception as e:
            return {"questions": [], "error": f"AI 服务不可用: {str(e)}"}

    # ── 内部方法 ──────────────────────────────────────────────

    def _build_system_prompt(self, context: dict) -> str:
        """组装 System Prompt"""
        chapter = context.get("chapter", {})
        user_progress = context.get("user_progress", {})
        ai_ctx = context.get("ai_context", {})
        errors = context.get("recent_errors", [])
        prereq = context.get("prerequisite_status", {})

        # 格式化错题
        errors_text = ""
        if errors:
            errors_text = "\n".join(
                f"- 题目 {e['question_id']}：学生回答 {e['user_answer']}"
                for e in errors[:5]
            )
        else:
            errors_text = "暂无错题记录"

        # 格式化前置知识
        prereq_text = ""
        if prereq:
            prereq_text = "\n".join(
                f"- {slug}：掌握度 {info.get('mastery', 0):.0%}"
                for slug, info in prereq.items()
            )
        else:
            prereq_text = "无前置知识要求"

        # 教案参考（简化版）
        ai_ctx_summary = json.dumps(
            {
                "topic": ai_ctx.get("topic_summary", ""),
                "key_insights": ai_ctx.get("key_insights", [])[:3],
                "common_mistakes": [
                    m.get("mistake", "") for m in ai_ctx.get("common_mistakes", [])[:3]
                ],
            },
            ensure_ascii=False,
            indent=2,
        )

        return f"""你是一位耐心且善于用多种方式讲解的初中数学和英语老师。

【学生当前状态】
- 正在学习：{chapter.get('title', '')}（{chapter.get('subject', '')}）
- 当前阶段：{chapter.get('current_stage', '')}
- 具体位置：{chapter.get('current_position', '')}
- 本章掌握度：{user_progress.get('mastery', 0):.0%}
- 练习正确率：{user_progress.get('practice_accuracy', 0):.0%}

【学生薄弱点】
{errors_text}

【前置知识掌握情况】
{prereq_text}

【教学参考】（你会用到但不需要全说）
{ai_ctx_summary}

【教学原则】
1. 不要直接给答案——引导学生自己发现
2. 如果学生说"没懂"，换一种方式解释（几何→代数→类比→举例，每次换角度）
3. 用初中生能理解的语言，避免术语堆砌
4. 回答末尾可以问一个引导性问题，确认学生是否真的懂了
5. 每次回答控制在 200 字以内，除非学生要求详细展开
"""

    def _calc_accuracy(self, db: Session, chapter_slug: str) -> float:
        """计算某个章节的答题正确率"""
        total = (
            db.query(QuestionAttempt)
            .filter(QuestionAttempt.node_slug == chapter_slug)
            .count()
        )
        if total == 0:
            return 0.0
        correct = (
            db.query(QuestionAttempt)
            .filter(
                QuestionAttempt.node_slug == chapter_slug,
                QuestionAttempt.is_correct == True,  # noqa: E712
            )
            .count()
        )
        return round(correct / total, 2)

    # ── 生成综合考试 ──────────────────────────────────────────

    async def generate_exam(
        self,
        chapters_data: list[dict],
        subject: str,
        question_count: int,
        difficulty_distribution: dict[int, int],
    ) -> list[dict]:
        """
        根据多个章节的教学内容生成综合考试题

        参数:
            chapters_data: [{"slug": str, "title": str, "ai_context": dict}, ...]
            subject: 学科 (math | english)
            question_count: 总题数
            difficulty_distribution: {1: n1, 2: n2, ...} 各难度题数

        返回:
            [{"stem": str, "options": list|null, "correct_answer": str,
              "explanation": str, "difficulty": int, "q_type": str,
              "chapter_slug": str}, ...]
        """
        # 1. 组装各章节的教学上下文
        chapters_summary_parts = []
        for ch in chapters_data:
            slug = ch.get("slug", "")
            title = ch.get("title", slug)
            ctx = ch.get("ai_context", {})

            key_insights = ctx.get("key_insights", [])
            mistakes = [
                m.get("mistake", "")
                for m in ctx.get("common_mistakes", [])[:3]
            ]
            templates = ctx.get("question_templates", {})

            parts = [f"### {title} ({slug})"]
            if ctx.get("topic_summary"):
                parts.append(f"主题概要: {ctx['topic_summary']}")
            if key_insights:
                parts.append(f"核心要点: {'; '.join(key_insights)}")
            if mistakes:
                parts.append(f"常见错误: {'; '.join(mistakes)}")
            if templates:
                template_str = "; ".join(
                    f"难度{k}: {v}" for k, v in templates.items()
                )
                parts.append(f"出题模板: {template_str}")
            chapters_summary_parts.append("\n".join(parts))

        chapters_summary = "\n\n".join(chapters_summary_parts)

        # 2. 难度分布描述
        dist_parts = []
        for d in sorted(difficulty_distribution.keys()):
            n = difficulty_distribution[d]
            if n > 0:
                dist_parts.append(f"难度{d}: {n}题")
        difficulty_desc = "、".join(dist_parts)
        subject_cn = "数学" if subject == "math" else "英语"

        # 3. 构建 Prompt
        system_prompt = f"""你是一位经验丰富的初中{subject_cn}出题老师。
请根据以下多个章节的教学内容，生成一套综合考试题。

【覆盖章节及教学内容】
{chapters_summary}

【出题要求】
- 总题数: {question_count}
- 难度分布: {difficulty_desc}
- 题型: 选择题(choice)和填空题(fill)混合，选择题约占60%
- 必须覆盖所有指定章节的知识点，每个章节至少一道题
- 每道题标注考察的章节 slug（chapter_slug 字段）
- 题目描述中的数学公式使用 LaTeX 格式（$...$ 或 $$...$$）
- 选择题的 options 格式: ["A: xxx", "B: xxx", "C: xxx", "D: xxx"]
- 每道题需包含详细的解题思路和答案解释（explanation 字段）
- 英语科目的话，题干和选项都使用英文

【JSON 输出格式】
返回一个 JSON 数组，每道题的结构如下：
{{
  "stem": "题目描述（支持 LaTeX）",
  "options": ["A: ...", "B: ...", "C: ...", "D: ..."],  // 选择题必填，填空题填 null
  "correct_answer": "正确答案（选择题填字母如A，填空题填答案）",
  "explanation": "解题思路和答案解释",
  "difficulty": 1-5,
  "q_type": "choice 或 fill",
  "chapter_slug": "考察的章节slug"
}}

只返回 JSON 数组，不要其他文字。"""

        # 4. 调用 LLM
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.7,
                max_tokens=8000,
            )
            content = response.choices[0].message.content or "[]"
            questions = self._parse_json_response(content)

            # 验证并修正题目
            validated = []
            for i, q in enumerate(questions):
                q_type = q.get("q_type", "fill")
                options = q.get("options")

                # 有 options → choice，无 → fill
                if options and isinstance(options, list) and len(options) >= 2:
                    q_type = "choice"
                else:
                    q_type = "fill"
                    options = None

                validated.append({
                    "stem": q.get("stem", ""),
                    "options": options,
                    "correct_answer": str(q.get("correct_answer", "")),
                    "explanation": q.get("explanation", ""),
                    "difficulty": max(1, min(5, int(q.get("difficulty", 1)))),
                    "q_type": q_type,
                    "chapter_slug": q.get("chapter_slug", ""),
                    "question_index": i + 1,
                })

            return validated

        except Exception as e:
            print(f"[AIOrchestrator] 考试生成失败: {e}")
            raise

    def _parse_json_response(self, content: str) -> list:
        """从 LLM 回复中提取 JSON 数组"""
        content = content.strip()
        # 去除 markdown 代码块
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return parsed
            # 有时返回的是 {questions: [...]}
            if isinstance(parsed, dict) and "questions" in parsed:
                return parsed["questions"]
            return []
        except json.JSONDecodeError:
            # 尝试从文本中提取 JSON 数组
            import re
            match = re.search(r"\[.*\]", content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
            return []

    def _format_errors(self, errors: list[dict]) -> str:
        """格式化错题列表"""
        if not errors:
            return "暂无错题记录"
        return "\n".join(
            f"- {e.get('question_id', '')}: {e.get('user_answer', '')}"
            for e in errors[:5]
        )
