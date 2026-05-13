"""
app/models/product.py
─────────────────────
Product model representing mobile phones in the shop.
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    # Numeric(10, 2) → up to 99,999,999.99 — suitable for phone prices
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=True)
    # Specs stored as plain text (e.g. "RAM: 8GB\nStorage: 128GB")
    specifications = Column(Text, nullable=True)
    # Relative URL path to uploaded image, e.g. /static/uploads/abc.jpg
    image = Column(String(500), nullable=True)
    stock = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name!r} brand={self.brand!r}>"
