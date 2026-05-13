"""
app/schemas/enquiry.py
──────────────────────
Pydantic schemas for the Enquiry model.
"""

from pydantic import BaseModel, Field
from datetime import datetime


class EnquiryCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=7, max_length=20)
    message: str = Field(..., min_length=5)


class EnquiryOut(BaseModel):
    id: int
    customer_name: str
    phone: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}
