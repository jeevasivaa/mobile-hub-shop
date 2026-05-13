"""
app/schemas/offer.py
────────────────────
Pydantic schemas for the Offer model.
"""

from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional


class OfferCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    discount_percentage: Decimal = Field(..., ge=0, le=100)
    active: bool = True


class OfferUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    active: Optional[bool] = None


class OfferOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    discount_percentage: Decimal
    image: Optional[str]
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
