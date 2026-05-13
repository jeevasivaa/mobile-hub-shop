"""
app/schemas/product.py
──────────────────────
Pydantic schemas for the Product model.
Used for input validation and serialization.
"""

from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional


class ProductCreate(BaseModel):
    """Schema for creating a new product."""
    name: str = Field(..., min_length=1, max_length=200)
    brand: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., gt=0, description="Price must be greater than 0")
    description: Optional[str] = None
    specifications: Optional[str] = None
    stock: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    """Schema for partial product updates — all fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = None
    specifications: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)


class ProductOut(BaseModel):
    """Schema for returning product data in responses."""
    id: int
    name: str
    brand: str
    price: Decimal
    description: Optional[str]
    specifications: Optional[str]
    image: Optional[str]
    stock: int
    created_at: datetime

    model_config = {"from_attributes": True}
