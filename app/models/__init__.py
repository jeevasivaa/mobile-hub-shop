"""
app/models/__init__.py
──────────────────────
Import all models here so Alembic can auto-detect them
when generating migration files.
"""

from app.models.user import User
from app.models.product import Product
from app.models.offer import Offer
from app.models.enquiry import Enquiry
