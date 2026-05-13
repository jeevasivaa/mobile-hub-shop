"""
app/main.py
────────────
FastAPI application entry point.
Uses absolute paths for Vercel serverless compatibility.
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import engine, direct_engine, Base
from app.routers import public, auth, admin

# Absolute path to the project root (works on both local and Vercel)
ROOT_DIR = Path(__file__).parent.parent
STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"


# ── Startup / Shutdown ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On startup:
    - Import all models so SQLAlchemy knows about them
    - Create DB tables if they don't exist (safe: won't overwrite)
    - Ensure upload directories exist (local only; Vercel uses ephemeral FS)
    """
    import app.models  # noqa: F401

    # Safely create tables — wrapped so a DB timeout won't crash the whole app
    try:
        Base.metadata.create_all(bind=direct_engine)
    except Exception as e:
        print(f"[WARNING] Could not create DB tables on startup: {e}")

    # Create upload dirs (only matters for local dev; Vercel FS is ephemeral)
    try:
        upload_base = Path(settings.UPLOAD_DIR)
        upload_base.mkdir(parents=True, exist_ok=True)
        (upload_base / "products").mkdir(exist_ok=True)
        (upload_base / "offers").mkdir(exist_ok=True)
    except Exception:
        pass  # Non-fatal on Vercel

    yield


# ── App Instance ──────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description="Mobile Phone Shop Website",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# ── Static Files ──────────────────────────────────────────────────────────────
# Use absolute path so it works on both local and Vercel

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ── Templates ────────────────────────────────────────────────────────────────
# Imported after defining ROOT_DIR so templates_config picks up the correct path
from app.templates_config import templates  # noqa: E402

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(public.router)
app.include_router(auth.router)
app.include_router(admin.router)

# ── Custom Error Handlers ─────────────────────────────────────────────────────

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(request, "404.html", {
        "settings": settings,
    }, status_code=404)


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return templates.TemplateResponse(request, "500.html", {
        "settings": settings,
    }, status_code=500)
