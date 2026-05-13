"""
app/services/enquiry_service.py
────────────────────────────────
Business logic for customer enquiry management.
"""

from sqlalchemy.orm import Session

from app.models.enquiry import Enquiry
from app.schemas.enquiry import EnquiryCreate


def submit_enquiry(db: Session, data: EnquiryCreate) -> Enquiry:
    """Save a new customer enquiry submitted via the contact form."""
    enquiry = Enquiry(
        customer_name=data.customer_name,
        phone=data.phone,
        message=data.message,
    )
    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)
    return enquiry


def get_all_enquiries(db: Session) -> list[Enquiry]:
    """Return all enquiries ordered by newest first (for admin panel)."""
    return db.query(Enquiry).order_by(Enquiry.created_at.desc()).all()


def get_enquiry_by_id(db: Session, enquiry_id: int) -> Enquiry | None:
    """Return a single enquiry by ID."""
    return db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()


def delete_enquiry(db: Session, enquiry: Enquiry) -> None:
    """Delete an enquiry record."""
    db.delete(enquiry)
    db.commit()
