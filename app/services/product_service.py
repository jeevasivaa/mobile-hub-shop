"""
app/services/product_service.py
────────────────────────────────
Business logic for product CRUD operations.
All database access goes through this service layer.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def get_all_products(db: Session, skip: int = 0, limit: int = 100) -> list[Product]:
    """Return all products ordered by newest first."""
    return (
        db.query(Product)
        .order_by(Product.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_featured_products(db: Session, limit: int = 8) -> list[Product]:
    """Return in-stock products for the homepage hero grid."""
    return (
        db.query(Product)
        .filter(Product.stock > 0)
        .order_by(Product.created_at.desc())
        .limit(limit)
        .all()
    )


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    """Return a single product by primary key, or None if not found."""
    return db.query(Product).filter(Product.id == product_id).first()


def search_products(db: Session, query: str = "", brand: str = "") -> list[Product]:
    """
    Search products by name/brand/description (case-insensitive).
    Optionally filter by exact brand name.
    """
    q = db.query(Product)

    if query and query.strip():
        term = f"%{query.strip()}%"
        q = q.filter(
            or_(
                Product.name.ilike(term),
                Product.brand.ilike(term),
                Product.description.ilike(term),
            )
        )

    if brand and brand.strip() and brand.lower() != "all":
        q = q.filter(Product.brand.ilike(f"%{brand.strip()}%"))

    return q.order_by(Product.name).all()


def get_brands(db: Session) -> list[str]:
    """Return a sorted list of unique brand names."""
    rows = db.query(Product.brand).distinct().order_by(Product.brand).all()
    return [row[0] for row in rows]


def create_product(
    db: Session,
    data: ProductCreate,
    image_path: Optional[str] = None,
) -> Product:
    """Create and persist a new product."""
    product = Product(
        name=data.name,
        brand=data.brand,
        price=data.price,
        description=data.description,
        specifications=data.specifications,
        stock=data.stock,
        image=image_path,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(
    db: Session,
    product: Product,
    data: ProductUpdate,
    image_path: Optional[str] = None,
) -> Product:
    """Apply partial updates to an existing product."""
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(product, field, value)

    # Only replace image if a new one was uploaded
    if image_path:
        product.image = image_path

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    """Permanently delete a product from the database."""
    db.delete(product)
    db.commit()
