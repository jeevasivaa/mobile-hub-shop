"""
app/main.py
────────────
FastAPI application entry point.
Registers all routers, mounts static files, and configures middleware.
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import engine, direct_engine, Base
from app.routers import public, auth, admin

# ── Startup / Shutdown ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Create all database tables on startup if they don't exist.
    In production use Alembic migrations instead.
    Also ensures the uploads directory exists.
    """
    # Import models so Base knows about them
    import app.models  # noqa: F401

    # Create tables (safe — won't overwrite existing)
    Base.metadata.create_all(bind=direct_engine)

    # Ensure uploads directory exists
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.UPLOAD_DIR + "/products").mkdir(exist_ok=True)
    Path(settings.UPLOAD_DIR + "/offers").mkdir(exist_ok=True)

    # Create .gitkeep so uploads dir is tracked by git
    gitkeep = Path(settings.UPLOAD_DIR) / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()

    yield
    # (cleanup code would go here if needed)


# ── App Instance ──────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description="Mobile Phone Shop Website",
    version="1.0.0",
    lifespan=lifespan,
    # Disable OpenAPI docs in production
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ── Middleware ────────────────────────────────────────────────────────────────

# Session middleware (used internally, not for admin — admin uses signed cookies)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# ── Static Files ──────────────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ── Templates (for 404 etc) ───────────────────────────────────────────────────

# ── Templates (for 404/500 error handlers) ───────────────────────────────────
from app.templates_config import templates

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
