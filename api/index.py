"""
api/index.py
─────────────
Vercel serverless entry point for the FastAPI app.
Vercel requires the ASGI app to be importable as 'app' from this file.
"""

import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app — Vercel will serve it via ASGI
from app.main import app  # noqa: F401 — Vercel uses this 'app' variable
