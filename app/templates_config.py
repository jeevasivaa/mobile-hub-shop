"""
app/templates_config.py
────────────────────────
Shared Jinja2Templates instance with absolute path.
Using absolute path ensures templates work on both local dev and Vercel.
"""

from pathlib import Path
from fastapi.templating import Jinja2Templates
from urllib.parse import quote as _url_quote

# Absolute path to templates dir — works regardless of CWD
TEMPLATES_DIR = Path(__file__).parent / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# ── Custom Filters ────────────────────────────────────────────────────────────
templates.env.filters["urlencode"] = lambda s: _url_quote(str(s), safe="")
