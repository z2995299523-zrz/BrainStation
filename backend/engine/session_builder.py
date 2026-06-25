"""6 步训练会话构建器"""
import json
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from ..config import config
from ..content.loader import ContentLoader
from ..models import DailySession, UserProgress
from .interleaver import generate_daily_mix
from .mastery import get_unlocked_nodes
from .path_planner import recommend_next_node


class SessionBuilder:
    """构建每日的 6 步训练会话"""

    def __init__(self, loader: ContentLoader):
        self.loader = loader

    def build_session(self, db: Session, session_date: str | None = None, subject: str | None = None) -> dict:
        """
        核心函数：构建或返回今天的训练会话

        参数 subject: "math" | "english" | None（全部）
        """
        if session_date is None:
            session_date = date.today().isoformat()

        # a. 检查是否有今日会话（按日期 + subject 区分）
        existing = (
            db.query(DailySession)
            .filter(
                DailySession.session_date == session_date,
                DailySession.subject == (subject or ""),
            )
            .first()
        )
        if existing:
            return self._build_response(db, existing, subject)

        # 跳过周末
        if config.training_flow.get("skip_weekends", True):
            today = date.fromisoformat(session_date)
            if today.weekday() >= 5:
                return {
                    "session_id": 0,
                    "session_date": session_date,
                    "day_number": 0,
                    "status": "weekend",
                    "target_node": None,
                    "subject": subject,
                    "steps": {},
                }

        # b. 确定目标节点（只取指定学科的）
        all_nodes_raw = self.loader.get_all_nodes()
        if subject:
            all_nodes = [n for n in all_nodes_raw if n.get("subject") == subject]
        else:
            all_nodes = all_nodes_raw
        all_progress = {
            p.node_slug: p for p in db.query(UserProgress).all()
        }
        unlocked = get_unlocked_nodes(
            all_nodes,
            all_progress,
            config.sm2.get("mastery_threshold", 0.85),
        )
        recommendation = recommend_next_node(all_nodes, all_progress, unlocked)
        target_slug = recommendation.get("slug")
        if target_slug is None and unlocked:
            target_slug = unlocked[0]
        if target_slug is None and all_nodes:
            target_slug = all_nodes[0]["slug"]

        # c. 获取需要复习的节点（只取指定学科的）
        today = session_date
        all_node_slugs = {n["slug"] for n in all_nodes}
        due_review = [
            p.node_slug
            for p in all_progress.values()
            if (
                p.next_review_at
                and p.next_review_at <= today
                and p.status in ("learning", "mastered")
                and p.node_slug in all_node_slugs
            )
        ]
        if not due_review:
            due_review = [s for s in unlocked if s != target_slug]

        # d. 生成题目（只取指定学科的）
        all_questions = self.loader.get_all_questions()
        if subject:
            all_questions = {
                slug: qs for slug, qs in all_questions.items()
                if slug in all_node_slugs
            }
        mix = generate_daily_mix(
            all_questions,
            target_slug or "",
            due_review,
            config.interleaving,
        )

        # e. 组装 trigger + learn + feynman
        target_node = self.loader.get_node(target_slug or "") if target_slug else None

        trigger_data: dict[str, Any] = {}
        learn_data: dict[str, Any] = {}
        feynman_data: dict[str, Any] = {}
        calibration_data: dict[str, Any] = {}

        if target_node:
            trigger = target_node.get("trigger", {})
            trigger_data = {
                "type": trigger.get("type", ""),
                "title": trigger.get("title", ""),
                "content": trigger.get("content", {}),
            }
            content = target_node.get("content", {})
            learn_data = {
                "node_title": target_node.get("title", ""),
                "subject": target_node.get("subject", ""),
                "operation": content.get("operation", {}),
                "understand": content.get("understand", {}),
                "connect": content.get("connect", {}),
                "interactives": target_node.get("interactives", []),
            }
            feynman = target_node.get("feynman", {})
            feynman_data = {
                "base_prompt": feynman.get("base_prompt", ""),
                "deep_questions": feynman.get("deep_questions", []),
                "key_elements": feynman.get("key_elements", []),
                "missing_hints": feynman.get("missing_hints", {}),
            }
            calibration_data = {
                "confidence_prompt": "今天学的内容你给自己打几分？（1-5）",
                "thought_card": target_node.get("thought_card", "今天学到了什么？"),
            }

        # f. 创建 daily_session 记录
        day_number = db.query(DailySession).count() + 1
        session = DailySession(
            session_date=session_date,
            subject=subject or "",
            day_number=day_number,
            status="in_progress",
            target_node=target_slug,
            started_at=date.today().isoformat(),
            steps_data=json.dumps({"subject": subject or ""}, ensure_ascii=False),
        )
        db.add(session)

        # 确保目标节点的 progress 存在
        if target_slug:
            existing_prog = (
                db.query(UserProgress)
                .filter(UserProgress.node_slug == target_slug)
                .first()
            )
            if not existing_prog:
                prog = UserProgress(
                    node_slug=target_slug,
                    status="unlocked",
                    mastery_level=0.0,
                    ef=config.sm2.get("initial_ef", 2.5),
                    created_at=date.today().isoformat(),
                    updated_at=date.today().isoformat(),
                )
                db.add(prog)
            elif existing_prog.status == "locked":
                existing_prog.status = "unlocked"
                existing_prog.updated_at = date.today().isoformat()

        db.commit()
        db.refresh(session)

        return self._build_response(db, session, subject)

    def _build_response(self, db: Session, session: DailySession, subject: str | None = None) -> dict:
        """组装 API 返回的 SessionData"""
        target_node = self.loader.get_node(session.target_node or "") if session.target_node else None

        # 按 subject 过滤节点
        all_nodes_raw = self.loader.get_all_nodes()
        if subject:
            all_nodes = [n for n in all_nodes_raw if n.get("subject") == subject]
        else:
            all_nodes = all_nodes_raw
        all_node_slugs = {n["slug"] for n in all_nodes}

        all_questions_raw = self.loader.get_all_questions()
        all_questions = {
            slug: qs for slug, qs in all_questions_raw.items()
            if not subject or slug in all_node_slugs
        }

        all_progress = {
            p.node_slug: p for p in db.query(UserProgress).all()
        }
        unlocked = get_unlocked_nodes(
            all_nodes, all_progress,
            config.sm2.get("mastery_threshold", 0.85),
        )

        due_review = [
            p.node_slug
            for p in all_progress.values()
            if (
                p.next_review_at
                and p.next_review_at <= session.session_date
                and p.status in ("learning", "mastered")
                and p.node_slug in all_node_slugs
            )
        ]
        if not due_review:
            due_review = [s for s in unlocked if s != session.target_node]

        mix = generate_daily_mix(
            all_questions,
            session.target_node or "",
            due_review,
            config.interleaving,
        )

        # trigger / learn / feynman
        trigger_data: dict[str, Any] = {}
        learn_data: dict[str, Any] = {}
        feynman_data: dict[str, Any] = {}
        calibration_data: dict[str, Any] = {}

        if target_node:
            trigger = target_node.get("trigger", {})
            trigger_data = {
                "type": trigger.get("type", ""),
                "title": trigger.get("title", ""),
                "content": trigger.get("content", {}),
            }
            content = target_node.get("content", {})
            learn_data = {
                "node_title": target_node.get("title", ""),
                "subject": target_node.get("subject", ""),
                "operation": content.get("operation", {}),
                "understand": content.get("understand", {}),
                "connect": content.get("connect", {}),
                "interactives": target_node.get("interactives", []),
            }
            feynman = target_node.get("feynman", {})
            feynman_data = {
                "base_prompt": feynman.get("base_prompt", ""),
                "deep_questions": feynman.get("deep_questions", []),
                "key_elements": feynman.get("key_elements", []),
                "missing_hints": feynman.get("missing_hints", {}),
            }
            calibration_data = {
                "confidence_prompt": "今天学的内容你给自己打几分？（1-5）",
                "thought_card": target_node.get("thought_card", "今天学到了什么？"),
            }

        return {
            "session_id": session.id,
            "session_date": session.session_date,
            "day_number": session.day_number,
            "status": session.status,
            "subject": subject,
            "target_node": target_node
            and {
                "slug": target_node["slug"],
                "title": target_node["title"],
                "subject": target_node["subject"],
                "tier": target_node.get("tier", ""),
            },
            "steps": {
                "trigger": trigger_data,
                "learn": learn_data,
                "checkup": {"questions": mix["checkup"]},
                "exam": {"questions": mix["exam"]},
                "feynman": feynman_data,
                "calibration": calibration_data,
            },
            "phases": {
                "learn": ["trigger", "learn", "checkup"],
                "test": ["exam", "feynman", "calibration"],
            },
        }
