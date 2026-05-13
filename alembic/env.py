"""
alembic/env.py
───────────────
Alembic migration environment.
Automatically detects all SQLAlchemy models and generates migrations.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add the project root to the Python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Base and all models so Alembic can detect schema changes
from app.core.database import Base
import app.models  # noqa: F401 — triggers all model imports

# Alembic Config object from alembic.ini
config = context.config

# Supabase: use DIRECT_URL for Alembic migrations.
# PgBouncer (transaction mode) blocks DDL statements like CREATE TABLE.
# DIRECT_URL connects directly to Postgres, bypassing PgBouncer.
direct_url = os.environ.get("DIRECT_URL") or os.environ.get("DATABASE_URL")
if direct_url:
    # Remove pgbouncer=true param if present — not needed for direct connection
    direct_url = direct_url.replace("?pgbouncer=true", "").replace("&pgbouncer=true", "")
    config.set_main_option("sqlalchemy.url", direct_url)

# Set up logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The metadata object containing all model table definitions
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Generates SQL scripts without connecting to the database.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    Connects to the database and applies migrations directly.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
