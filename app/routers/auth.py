"""
app/routers/auth.py
────────────────────
Admin login/logout routes. Uses new Starlette TemplateResponse API.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_session_token
from app.core.config import settings
from app.templates_config import templates
from app.models.user import User

router = APIRouter()


@router.get("/admin/login", response_class=HTMLResponse, name="admin_login")
def login_page(request: Request):
    if request.cookies.get("session_token"):
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return templates.TemplateResponse(request, "admin/login.html", {
        "settings": settings,
        "page_title": "Admin Login",
    })


@router.post("/admin/login", response_class=HTMLResponse, name="admin_login_post")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request, "admin/login.html", {
            "settings": settings,
            "error": "Invalid username or password.",
            "page_title": "Admin Login",
        })

    token = create_session_token(user.id)
    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=86400,
        secure=False,
    )
    return response


@router.post("/admin/logout", name="admin_logout")
def logout():
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("session_token")
    return response
