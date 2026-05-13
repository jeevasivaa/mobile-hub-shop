"""
app/services/offer_service.py
──────────────────────────────
Business logic for offer/promotion management.
"""

from sqlalchemy.orm import Session
from typing import Optional

from app.models.offer import Offer
from app.schemas.offer import OfferCreate, OfferUpdate


def get_active_offers(db: Session) -> list[Offer]:
    """Return all active offers for the public offers page."""
    return (
        db.query(Offer)
        .filter(Offer.active == True)
        .order_by(Offer.id.desc())
        .all()
    )


def get_all_offers(db: Session) -> list[Offer]:
    """Return all offers (active and inactive) for admin panel."""
    return db.query(Offer).order_by(Offer.id.desc()).all()


def get_offer_by_id(db: Session, offer_id: int) -> Optional[Offer]:
    """Return a single offer by ID, or None if not found."""
    return db.query(Offer).filter(Offer.id == offer_id).first()


def create_offer(
    db: Session,
    data: OfferCreate,
    image_path: Optional[str] = None,
) -> Offer:
    """Create and persist a new offer."""
    offer = Offer(
        title=data.title,
        description=data.description,
        discount_percentage=data.discount_percentage,
        active=data.active,
        image=image_path,
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


def update_offer(
    db: Session,
    offer: Offer,
    data: OfferUpdate,
    image_path: Optional[str] = None,
) -> Offer:
    """Apply partial updates to an existing offer."""
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(offer, field, value)

    if image_path:
        offer.image = image_path

    db.commit()
    db.refresh(offer)
    return offer


def toggle_offer_active(db: Session, offer: Offer) -> Offer:
    """Toggle an offer between active and inactive."""
    offer.active = not offer.active
    db.commit()
    db.refresh(offer)
    return offer


def delete_offer(db: Session, offer: Offer) -> None:
    """Permanently delete an offer."""
    db.delete(offer)
    db.commit()
