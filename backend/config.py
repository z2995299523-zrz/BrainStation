"""配置加载 + 热重载（watchdog 监听 config.yaml）"""
import os
from pathlib import Path
from typing import Any

import yaml


class Config:
    """从 config.yaml 加载配置，支持属性访问和热重载"""

    def __init__(self, config_path: str = "config.yaml"):
        self._config_path = Path(config_path)
        self._data: dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        """重新加载配置文件"""
        if not self._config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self._config_path}")
        with open(self._config_path, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f)

    @property
    def app(self) -> dict:
        return self._data.get("app", {})

    @property
    def sm2(self) -> dict:
        return self._data.get("sm2", {})

    @property
    def training_flow(self) -> dict:
        return self._data.get("training_flow", {})

    @property
    def interleaving(self) -> dict:
        return self._data.get("interleaving", {})

    @property
    def adaptive_path(self) -> dict:
        return self._data.get("adaptive_path", {})

    @property
    def feynman(self) -> dict:
        return self._data.get("feynman", {})

    @property
    def difficulty(self) -> dict:
        return self._data.get("difficulty", {})

    @property
    def data(self) -> dict:
        return self._data

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)


# 全局单例
config = Config()
