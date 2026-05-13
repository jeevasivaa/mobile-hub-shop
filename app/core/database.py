"""
app/core/database.py
────────────────────
SQLAlchemy database engine, session factory, and Base model class.

Notes for Supabase:
- DATABASE_URL uses PgBouncer (port 6543) — great for app queries.
- DIRECT_URL connects directly to Postgres (port 5432) — required for DDL.
- psycopg2 does not support the ?pgbouncer=true param, so we strip it.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


def _clean_url(url: str) -> str:
    """Remove Prisma-specific params (pgbouncer=true) that psycopg2 rejects."""
    return url.replace("?pgbouncer=true", "").replace("&pgbouncer=true", "")


# ── App Engine (PgBouncer pooler — for all route queries) ─────────────────────
engine = create_engine(
    _clean_url(settings.DATABASE_URL),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# ── Direct Engine (bypasses PgBouncer — for DDL like CREATE TABLE) ────────────
# Used by main.py startup (Base.metadata.create_all)
_direct_url = settings.DIRECT_URL or settings.DATABASE_URL
direct_engine = create_engine(
    _clean_url(_direct_url),
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=2,
)

# ── Session Factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Declarative Base ──────────────────────────────────────────────────────────
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session.
    Ensures the session is properly closed after each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
