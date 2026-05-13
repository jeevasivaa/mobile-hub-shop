"""
app/utils/file_upload.py
─────────────────────────
Utility functions for handling file uploads.

On Vercel (read-only filesystem):
- File uploads to /tmp work but are EPHEMERAL (lost on redeploy/restart)
- Use an image_url field instead for permanent images

On local dev / VPS:
- Files are saved to app/static/uploads/
"""

import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile

from app.core.config import settings


# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Detect Vercel environment (read-only filesystem except /tmp)
IS_VERCEL = os.environ.get("VERCEL") == "1" or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None


def save_upload_file(file: UploadFile, subfolder: str = "") -> str:
    """
    Save an uploaded image file.

    On Vercel: saves to /tmp (ephemeral — not served publicly).
    On local/VPS: saves to app/static/uploads/ (served at /static/uploads/).

    Returns:
        URL path string on local, or None-ish signal on Vercel (use image_url instead).

    Raises:
        ValueError: If the file extension is not allowed.
    """
    original_name = file.filename or ""
    ext = Path(original_name).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(ALLOWED_EXTENSIONS)
        raise ValueError(f"File type '{ext}' not allowed. Allowed: {allowed}")

    unique_name = f"{uuid.uuid4().hex}{ext}"

    if IS_VERCEL:
        # Save to /tmp (writable on Vercel) — but this is ephemeral
        # In production, the caller should prefer image_url over file upload
        tmp_dir = Path("/tmp") / (subfolder or "uploads")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        file_path = tmp_dir / unique_name
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Return None — ephemeral path can't be served as a public URL on Vercel
        return None  # type: ignore[return-value]
    else:
        # Local / VPS — save to static/uploads/
        upload_dir = Path(settings.UPLOAD_DIR)
        if subfolder:
            upload_dir = upload_dir / subfolder
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / unique_name
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        if subfolder:
            return f"/static/uploads/{subfolder}/{unique_name}"
        return f"/static/uploads/{unique_name}"


def delete_upload_file(file_url: str) -> None:
    """Delete a previously uploaded file given its URL path (local only)."""
    if not file_url or IS_VERCEL:
        return
    # Only delete local /static/uploads/ paths
    if not file_url.startswith("/static/uploads/"):
        return
    relative = file_url.lstrip("/")
    full_path = Path("app") / relative
    if full_path.exists() and full_path.is_file():
        full_path.unlink()
