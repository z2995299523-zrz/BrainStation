#!/usr/bin/env python
"""一键启动：初中数英思维训练营"""
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent


def main():
    os.chdir(ROOT)

    # 1. 确保 data 目录存在
    (ROOT / "data").mkdir(exist_ok=True)

    # 2. 初始化数据库（首次启动自动建表）
    print("🔧 初始化数据库...")
    from backend.database import init_db
    init_db()
    print("✅ 数据库就绪")

    # 3. 加载内容
    print("📚 加载内容...")
    from backend.content.loader import ContentLoader
    loader = ContentLoader(str(ROOT / "content"))
    loader.load_all()
    nodes = len(loader.get_all_nodes())
    questions = sum(len(v) for v in loader.get_all_questions().values())
    print(f"✅ 加载完成：{nodes} 个节点, {questions} 道题目")

    # 4. 启动服务
    print("🚀 启动服务 http://localhost:8000 ...")
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
