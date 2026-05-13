"""
app/core/security.py
────────────────────
Password hashing using bcrypt directly (bypasses passlib compatibility issues
with bcrypt 4.x/5.x) and session token signing using itsdangerous.
"""

import bcrypt
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from app.core.config import settings


# ── Password Hashing ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt. Returns a UTF-8 string."""
    pwd_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.
    Returns True if they match, False otherwise.
    """
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ── Session Tokens ────────────────────────────────────────────────────────────
# URLSafeTimedSerializer signs data with the SECRET_KEY and embeds a timestamp.
# Stored as an httpOnly cookie — safe from XSS attacks.
_serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def create_session_token(user_id: int) -> str:
    """Create a cryptographically signed session token containing the user ID."""
    return _serializer.dumps({"user_id": user_id}, salt="admin-session")


def verify_session_token(token: str, max_age: int = 86400) -> dict | None:
    """
    Decode and verify a session token.

    Args:
        token:   The signed token string from the cookie.
        max_age: Token validity in seconds. Default = 24 hours.

    Returns:
        The decoded payload dict or None if invalid/expired.
    """
    try:
        return _serializer.loads(token, salt="admin-session", max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
