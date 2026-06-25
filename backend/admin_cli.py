"""管理员账号管理脚本

用法:
  python -m backend.admin_cli create <username> <password>   # 创建管理员
  python -m backend.admin_cli promote <username>             # 升级已有用户为管理员
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
import bcrypt
from backend.database import SessionLocal, init_db
from backend.models import User


def create_admin(username: str, password: str):
    """创建新管理员账号"""
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"用户 '{username}' 已存在，当前角色: {existing.role}")
            if existing.role != "admin":
                existing.role = "admin"
                db.commit()
                print(f"已升级为管理员。")
            else:
                print("该用户已经是管理员。")
            return

        now = datetime.now(timezone.utc).isoformat()
        user = User(
            username=username,
            hashed_password=bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8"),
            role="admin",
            created_at=now,
        )
        db.add(user)
        db.commit()
        print(f"管理员 '{username}' 创建成功！")
    finally:
        db.close()


def promote_user(username: str):
    """升级已有用户为管理员"""
    init_db()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"用户 '{username}' 不存在，请先注册。")
            return
        if user.role == "admin":
            print(f"用户 '{username}' 已经是管理员。")
            return
        user.role = "admin"
        db.commit()
        print(f"用户 '{username}' 已升级为管理员。")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "create" and len(sys.argv) >= 4:
        create_admin(sys.argv[2], sys.argv[3])
    elif cmd == "promote" and len(sys.argv) >= 3:
        promote_user(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
