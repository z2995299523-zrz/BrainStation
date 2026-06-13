"""YAML 内容加载器 —— 加载知识节点和题目"""
from pathlib import Path
from typing import Any

import yaml


class ContentLoader:
    """遍历 content/nodes/ 和 content/questions/ 加载所有 YAML 文件"""

    def __init__(self, content_dir: str = "content"):
        self._content_dir = Path(content_dir)
        self._nodes: dict[str, dict] = {}        # {slug: node_data}
        self._questions: dict[str, list[dict]] = {}  # {slug: [question]}
        self._loaded = False

    def load_all(self) -> None:
        """加载所有内容文件"""
        self._nodes.clear()
        self._questions.clear()

        # 加载知识节点
        nodes_dir = self._content_dir / "nodes"
        if nodes_dir.exists():
            for yaml_file in nodes_dir.rglob("*.yaml"):
                data = self._load_yaml(yaml_file)
                if data and "slug" in data:
                    self._nodes[data["slug"]] = data

        # 加载题目
        questions_dir = self._content_dir / "questions"
        if questions_dir.exists():
            for yaml_file in questions_dir.rglob("*.yaml"):
                data = self._load_yaml(yaml_file)
                if data and "node_slug" in data and "questions" in data:
                    slug = data["node_slug"]
                    if slug not in self._questions:
                        self._questions[slug] = []
                    self._questions[slug].extend(data["questions"])

        self._loaded = True

    def reload(self) -> None:
        """清空缓存并重新加载"""
        self._nodes.clear()
        self._questions.clear()
        self._loaded = False
        self.load_all()

    def get_node(self, slug: str) -> dict | None:
        """获取单个节点"""
        return self._nodes.get(slug)

    def get_questions(self, slug: str) -> list[dict]:
        """获取某节点的所有题目"""
        return self._questions.get(slug, [])

    def get_all_nodes(self) -> list[dict]:
        """
        返回所有节点的摘要信息
        [{slug, title, subject, tier, prerequisites}]
        """
        return [
            {
                "slug": slug,
                "title": node.get("title", slug),
                "subject": node.get("subject", ""),
                "tier": node.get("tier", ""),
                "prerequisites": node.get("prerequisites", []),
            }
            for slug, node in self._nodes.items()
        ]

    def get_all_questions(self) -> dict[str, list[dict]]:
        """返回 {slug: [questions]}"""
        return dict(self._questions)

    def _load_yaml(self, path: Path) -> dict[str, Any] | None:
        """加载单个 YAML 文件"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[WARN] Failed to load {path}: {e}")
            return None
