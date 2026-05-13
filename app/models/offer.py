"""
app/models/offer.py
───────────────────
Offer/promotion model for special deals on products.
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    # discount_percentage: 0.00 to 100.00
    discount_percentage = Column(Numeric(5, 2), nullable=False)
    image = Column(String(500), nullable=True)
    # Only active offers are shown on the public site
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Offer id={self.id} title={self.title!r} active={self.active}>"
