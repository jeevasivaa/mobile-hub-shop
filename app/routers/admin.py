"""
app/routers/admin.py
─────────────────────
Admin panel routes. All protected by get_current_admin dependency.
Uses new Starlette TemplateResponse(request, name, context) API.
"""

from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.templates_config import templates
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.models.product import Product
from app.models.offer import Offer
from app.models.enquiry import Enquiry
from app.services import product_service, offer_service, enquiry_service
from app.schemas.product import ProductCreate, ProductUpdate
from app.schemas.offer import OfferCreate, OfferUpdate
from app.utils.file_upload import save_upload_file, delete_upload_file

router = APIRouter(prefix="/admin")


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_class=HTMLResponse, name="admin_dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin

    total_products = db.query(Product).count()
    total_offers = db.query(Offer).count()
    total_enquiries = db.query(Enquiry).count()
    recent_enquiries = enquiry_service.get_all_enquiries(db)[:5]

    return templates.TemplateResponse(request, "admin/dashboard.html", {
        "admin": admin,
        "settings": settings,
        "total_products": total_products,
        "total_offers": total_offers,
        "total_enquiries": total_enquiries,
        "recent_enquiries": recent_enquiries,
        "page_title": "Admin Dashboard",
    })


# ── Products List & Create ────────────────────────────────────────────────────

@router.get("/products", response_class=HTMLResponse, name="admin_products")
def admin_products(
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin
    products = product_service.get_all_products(db)
    return templates.TemplateResponse(request, "admin/products.html", {
        "admin": admin, "products": products,
        "settings": settings, "page_title": "Manage Products",
    })


@router.get("/products/new", response_class=HTMLResponse, name="admin_product_new")
def admin_product_new(
    request: Request, admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin
    return templates.TemplateResponse(request, "admin/product_form.html", {
        "admin": admin, "product": None,
        "settings": settings, "page_title": "Add Product",
    })


@router.post("/products/new", name="admin_product_create")
async def admin_product_create(
    request: Request,
    name: str = Form(...), brand: str = Form(...), price: float = Form(...),
    description: str = Form(""), specifications: str = Form(""), stock: int = Form(0),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin

    image_path = None
    if image and image.filename:
        try:
            image_path = save_upload_file(image, subfolder="products")
        except ValueError as e:
            return templates.TemplateResponse(request, "admin/product_form.html", {
                "admin": admin, "product": None,
                "settings": settings, "error": str(e), "page_title": "Add Product",
            })

    data = ProductCreate(
        name=name, brand=brand, price=price,
        description=description or None,
        specifications=specifications or None, stock=stock,
    )
    product_service.create_product(db, data, image_path)
    return RedirectResponse(url="/admin/products", status_code=302)


@router.get("/products/{product_id}/edit", response_class=HTMLResponse, name="admin_product_edit")
def admin_product_edit(
    request: Request, product_id: int,
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return templates.TemplateResponse(request, "admin/product_form.html", {
        "admin": admin, "product": product,
        "settings": settings, "page_title": f"Edit: {product.name}",
    })


@router.post("/products/{product_id}/edit", name="admin_product_update")
async def admin_product_update(
    request: Request, product_id: int,
    name: str = Form(...), brand: str = Form(...), price: float = Form(...),
    description: str = Form(""), specifications: str = Form(""), stock: int = Form(0),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    image_path = None
    if image and image.filename:
        try:
            if product.image:
                delete_upload_file(product.image)
            image_path = save_upload_file(image, subfolder="products")
        except ValueError as e:
            return templates.TemplateResponse(request, "admin/product_form.html", {
                "admin": admin, "product": product,
                "settings": settings, "error": str(e),
                "page_title": f"Edit: {product.name}",
            })

    data = ProductUpdate(
        name=name, brand=brand, price=price,
        description=description or None,
        specifications=specifications or None, stock=stock,
    )
    product_service.update_product(db, product, data, image_path)
    return RedirectResponse(url="/admin/products", status_code=302)


@router.delete("/products/{product_id}", response_class=HTMLResponse, name="admin_product_delete")
def admin_product_delete(
    request: Request, product_id: int,
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin
    product = product_service.get_product_by_id(db, product_id)
    if product:
        if product.image:
            delete_upload_file(product.image)
        product_service.delete_product(db, product)
    return HTMLResponse(content="", status_code=200)


# ── Offers ────────────────────────────────────────────────────────────────────

@router.get("/offers", response_class=HTMLResponse, name="admin_offers")
def admin_offers(
    request: Request,
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin
    offers = offer_service.get_all_offers(db)
    return templates.TemplateResponse(request, "admin/offers.html", {
        "admin": admin, "offers": offers,
        "settings": settings, "page_title": "Manage Offers",
    })


@router.get("/offers/new", response_class=HTMLResponse, name="admin_offer_new")
def admin_offer_new(request: Request, admin: User = Depends(get_current_admin)):
    if isinstance(admin, RedirectResponse):
        return admin
    return templates.TemplateResponse(request, "admin/offer_form.html", {
        "admin": admin, "offer": None,
        "settings": settings, "page_title": "Add Offer",
    })


@router.post("/offers/new", name="admin_offer_create")
async def admin_offer_create(
    request: Request,
    title: str = Form(...), description: str = Form(""),
    discount_percentage: float = Form(...), active: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin
    image_path = None
    if image and image.filename:
        try:
            image_path = save_upload_file(image, subfolder="offers")
        except ValueError as e:
            return templates.TemplateResponse(request, "admin/offer_form.html", {
                "admin": admin, "offer": None,
                "settings": settings, "error": str(e), "page_title": "Add Offer",
            })
    data = OfferCreate(
        title=title, description=description or None,
        discount_percentage=discount_percentage, active=(active == "on"),
    )
    offer_service.create_offer(db, data, image_path)
    return RedirectResponse(url="/admin/offers", status_code=302)


@router.get("/offers/{offer_id}/edit", response_class=HTMLResponse, name="admin_offer_edit")
def admin_offer_edit(
    request: Request, offer_id: int,
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin
    offer = offer_service.get_offer_by_id(db, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return templates.TemplateResponse(request, "admin/offer_form.html", {
        "admin": admin, "offer": offer,
        "settings": settings, "page_title": f"Edit: {offer.title}",
    })


@router.post("/offers/{offer_id}/edit", name="admin_offer_update")
async def admin_offer_update(
    request: Request, offer_id: int,
    title: str = Form(...), description: str = Form(""),
    discount_percentage: float = Form(...), active: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin
    offer = offer_service.get_offer_by_id(db, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    image_path = None
    if image and image.filename:
        try:
            if offer.image:
                delete_upload_file(offer.image)
            image_path = save_upload_file(image, subfolder="offers")
        except ValueError as e:
            return templates.TemplateResponse(request, "admin/offer_form.html", {
                "admin": admin, "offer": offer,
                "settings": settings, "error": str(e),
                "page_title": f"Edit: {offer.title}",
            })
    data = OfferUpdate(
        title=title, description=description or None,
        discount_percentage=discount_percentage, active=(active == "on"),
    )
    offer_service.update_offer(db, offer, data, image_path)
    return RedirectResponse(url="/admin/offers", status_code=302)


@router.delete("/offers/{offer_id}", response_class=HTMLResponse, name="admin_offer_delete")
def admin_offer_delete(
    request: Request, offer_id: int,
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin
    offer = offer_service.get_offer_by_id(db, offer_id)
    if offer:
        if offer.image:
            delete_upload_file(offer.image)
        offer_service.delete_offer(db, offer)
    return HTMLResponse(content="", status_code=200)


# ── Enquiries ─────────────────────────────────────────────────────────────────

@router.get("/enquiries", response_class=HTMLResponse, name="admin_enquiries")
def admin_enquiries(
    request: Request,
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin
    enquiries = enquiry_service.get_all_enquiries(db)
    return templates.TemplateResponse(request, "admin/enquiries.html", {
        "admin": admin, "enquiries": enquiries,
        "settings": settings, "page_title": "Customer Enquiries",
    })


@router.delete("/enquiries/{enquiry_id}", response_class=HTMLResponse, name="admin_enquiry_delete")
def admin_enquiry_delete(
    request: Request, enquiry_id: int,
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin),
):
    if isinstance(admin, RedirectResponse):
        return admin
    enquiry = enquiry_service.get_enquiry_by_id(db, enquiry_id)
    if enquiry:
        enquiry_service.delete_enquiry(db, enquiry)
    return HTMLResponse(content="", status_code=200)
