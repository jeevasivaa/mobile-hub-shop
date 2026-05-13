"""
app/templates_config.py
────────────────────────
Shared Jinja2Templates instance used across all routers.
Centralised so custom filters are registered once.
"""

from fastapi.templating import Jinja2Templates
from urllib.parse import quote as _url_quote

# Single shared templates instance
templates = Jinja2Templates(directory="app/templates")

# ── Custom Filters ────────────────────────────────────────────────────────────
# urlencode: URL-encode a string (e.g. for WhatsApp message links)
templates.env.filters["urlencode"] = lambda s: _url_quote(str(s), safe="")
