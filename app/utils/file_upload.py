"""
app/utils/file_upload.py
─────────────────────────
Utility functions for handling file uploads.
Saves images to the local static/uploads directory.

To switch to Supabase Storage or S3 in production,
replace save_upload_file() — the rest of the app stays the same.
"""

import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile

from app.core.config import settings


# Only allow safe image file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def save_upload_file(file: UploadFile, subfolder: str = "") -> str:
    """
    Save an uploaded image file to the uploads directory.

    Args:
        file:      The UploadFile object from the form submission.
        subfolder: Optional subdirectory under uploads/ (e.g. "products").

    Returns:
        The URL-friendly path to the saved file (e.g. /static/uploads/products/abc123.jpg).

    Raises:
        ValueError: If the file extension is not allowed.
    """
    # Validate extension
    original_name = file.filename or ""
    ext = Path(original_name).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(ALLOWED_EXTENSIONS)
        raise ValueError(f"File type '{ext}' is not allowed. Allowed types: {allowed}")

    # Generate a unique filename to prevent conflicts and directory traversal
    unique_name = f"{uuid.uuid4().hex}{ext}"

    # Build the filesystem path
    upload_dir = Path(settings.UPLOAD_DIR)
    if subfolder:
        upload_dir = upload_dir / subfolder

    # Create directories if they don't exist
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / unique_name

    # Write the file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Return the URL path (relative to the app root, served as /static/...)
    if subfolder:
        return f"/static/uploads/{subfolder}/{unique_name}"
    return f"/static/uploads/{unique_name}"


def delete_upload_file(file_url: str) -> None:
    """
    Delete a previously uploaded file given its URL path.

    Args:
        file_url: The URL path as returned by save_upload_file(),
                  e.g. /static/uploads/products/abc123.jpg
    """
    if not file_url:
        return

    # Convert URL path (/static/uploads/...) to filesystem path (app/static/uploads/...)
    # Strip leading slash and prepend 'app/'
    relative = file_url.lstrip("/")
    full_path = Path("app") / relative

    if full_path.exists() and full_path.is_file():
        full_path.unlink()
