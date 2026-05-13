"""
app/routers/public.py
──────────────────────
All public-facing routes. Uses new Starlette TemplateResponse API
where request= is a keyword argument (Starlette 1.x).
"""

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.templates_config import templates
from app.services import product_service, offer_service, enquiry_service
from app.schemas.enquiry import EnquiryCreate

router = APIRouter()


# ── Home Page ─────────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse, name="home")
def home(request: Request, db: Session = Depends(get_db)):
    products = product_service.get_featured_products(db, limit=8)
    offers = offer_service.get_active_offers(db)
    return templates.TemplateResponse(request, "index.html", {
        "products": products,
        "offers": offers,
        "settings": settings,
        "page_title": f"{settings.APP_NAME} - Best Mobile Phones",
        "meta_description": f"Explore the latest smartphones at {settings.APP_NAME}. Best prices, top brands.",
    })


# ── About Page ────────────────────────────────────────────────────────────────

@router.get("/about", response_class=HTMLResponse, name="about")
def about(request: Request):
    return templates.TemplateResponse(request, "about.html", {
        "settings": settings,
        "page_title": f"About Us - {settings.APP_NAME}",
        "meta_description": f"Learn about {settings.APP_NAME}, your trusted local mobile phone store.",
    })


# ── Products Page ─────────────────────────────────────────────────────────────

@router.get("/products", response_class=HTMLResponse, name="products")
def products(
    request: Request,
    q: str = "",
    brand: str = "",
    db: Session = Depends(get_db),
):
    products_list = product_service.search_products(db, query=q, brand=brand)
    brands = product_service.get_brands(db)

    # HTMX partial — return only the product grid
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(request, "partials/product_cards.html", {
            "products": products_list,
            "settings": settings,
        })

    return templates.TemplateResponse(request, "products.html", {
        "products": products_list,
        "brands": brands,
        "selected_brand": brand,
        "query": q,
        "settings": settings,
        "page_title": f"Products - {settings.APP_NAME}",
        "meta_description": "Browse our wide selection of mobile phones from top brands.",
    })


# ── Product Detail Page ───────────────────────────────────────────────────────

@router.get("/products/{product_id}", response_class=HTMLResponse, name="product_detail")
def product_detail(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product_by_id(db, product_id)

    if not product:
        return templates.TemplateResponse(request, "404.html", {
            "settings": settings,
        }, status_code=404)

    related = product_service.search_products(db, brand=product.brand)
    related = [p for p in related if p.id != product_id][:4]

    return templates.TemplateResponse(request, "product_detail.html", {
        "product": product,
        "related": related,
        "settings": settings,
        "page_title": f"{product.name} - {settings.APP_NAME}",
        "meta_description": product.description or f"Buy {product.name} at the best price.",
    })


# ── Offers Page ───────────────────────────────────────────────────────────────

@router.get("/offers", response_class=HTMLResponse, name="offers")
def offers(request: Request, db: Session = Depends(get_db)):
    offers_list = offer_service.get_active_offers(db)
    return templates.TemplateResponse(request, "offers.html", {
        "offers": offers_list,
        "settings": settings,
        "page_title": f"Offers & Deals - {settings.APP_NAME}",
        "meta_description": "Exclusive deals and discounts on top mobile phones.",
    })


# ── Contact Page ──────────────────────────────────────────────────────────────

@router.get("/contact", response_class=HTMLResponse, name="contact")
def contact_page(request: Request):
    return templates.TemplateResponse(request, "contact.html", {
        "settings": settings,
        "page_title": f"Contact Us - {settings.APP_NAME}",
        "meta_description": f"Contact {settings.APP_NAME} for enquiries, support, or store visit.",
    })


@router.post("/contact", response_class=HTMLResponse, name="contact_submit")
def contact_submit(
    request: Request,
    customer_name: str = Form(...),
    phone: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = EnquiryCreate(customer_name=customer_name, phone=phone, message=message)
        enquiry_service.submit_enquiry(db, data)
        return templates.TemplateResponse(request, "partials/enquiry_success.html", {
            "settings": settings,
        })
    except Exception:
        return templates.TemplateResponse(request, "partials/enquiry_error.html", {
            "settings": settings,
            "error": "Something went wrong. Please try again.",
        })
