"""
app/core/config.py
──────────────────
Central configuration using pydantic-settings.
All settings are read from environment variables or .env file.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────
    DATABASE_URL: str
    # DIRECT_URL is used by Alembic for migrations (bypasses PgBouncer)
    DIRECT_URL: str = ""

    # ── Security ──────────────────────────────────────────
    SECRET_KEY: str = "change-this-in-production"

    # ── App ───────────────────────────────────────────────
    APP_NAME: str = "MobileHub"
    DEBUG: bool = False
    BASE_URL: str = "http://localhost:8000"

    # ── Shop Info ─────────────────────────────────────────
    WHATSAPP_NUMBER: str = "+910000000000"
    SHOP_ADDRESS: str = "123 Main Street, City, State 000000"
    GOOGLE_MAPS_EMBED_URL: str = (
        "https://maps.google.com/maps?q=india&output=embed"
    )

    # ── File Uploads ──────────────────────────────────────
    UPLOAD_DIR: str = "app/static/uploads"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",   # Ignore unknown env vars — prevents startup crashes
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — only reads .env once."""
    return Settings()


# Convenience singleton used across the app
settings = get_settings()
