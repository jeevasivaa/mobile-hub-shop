"""
create_admin.py
────────────────
One-time script to create the first admin user.
Run this after setting up the database.

Usage:
    python create_admin.py
"""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def create_admin(username: str, password: str) -> None:
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"✅ Admin '{username}' already exists.")
            return

        admin = User(
            username=username,
            password_hash=hash_password(password),
        )
        db.add(admin)
        db.commit()
        print(f"✅ Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Login at: /admin/login")
    finally:
        db.close()


if __name__ == "__main__":
    print("=== MobileHub Admin User Setup ===\n")
    username = input("Enter admin username (default: admin): ").strip() or "admin"
    password = input("Enter admin password: ").strip()

    if len(password) < 6:
        print("❌ Password must be at least 6 characters.")
        sys.exit(1)

    create_admin(username, password)
