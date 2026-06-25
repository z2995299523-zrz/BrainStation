#!/usr/bin/env python
"""一键启动：初中数英思维训练营"""
import sys
import os
from pathlib import Path

# 强制 UTF-8 输出（Windows 兼容）
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent


def main():
    os.chdir(ROOT)

    # 0. 加载 .env 文件（如果存在）
    env_file = ROOT / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    if key.strip() and key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()
        print("[ENV] .env 已加载")

    # 1. 确保 data 目录存在
    (ROOT / "data").mkdir(exist_ok=True)

    # 2. 初始化数据库（首次启动自动建表）
    print("[INIT] 初始化数据库...")
    from backend.database import init_db
    init_db()
    print("[OK] 数据库就绪")

    # 3. 加载内容
    print("[LOAD] 加载内容...")
    from backend.content.loader import ContentLoader
    loader = ContentLoader(str(ROOT / "content"))
    loader.load_all()
    nodes = len(loader.get_all_nodes())
    questions = sum(len(v) for v in loader.get_all_questions().values())
    print(f"[OK] 加载完成：{nodes} 个节点, {questions} 道题目")

    # 4. 启动服务
    print("[START] 启动服务 http://localhost:8000 ...")
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
