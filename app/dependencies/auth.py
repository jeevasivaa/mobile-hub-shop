"""
app/dependencies/auth.py
─────────────────────────
Admin authentication dependency.
Reads the session cookie, validates it, and returns the current admin user.
If not authenticated, redirects to the login page.
"""

from fastapi import Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_session_token
from app.models.user import User


def get_current_admin(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency that enforces admin authentication.

    Flow:
      1. Read 'session_token' from the request cookies.
      2. Verify the token's signature and expiry using SECRET_KEY.
      3. Load the corresponding User from the database.
      4. Return the User object if valid.
      5. Redirect to /admin/login if any step fails.

    Usage in a route:
        @router.get("/admin/dashboard")
        def dashboard(admin: User = Depends(get_current_admin)):
            ...
    """
    token = request.cookies.get("session_token")

    if not token:
        return RedirectResponse(url="/admin/login", status_code=302)

    payload = verify_session_token(token)
    if not payload:
        # Token expired or tampered
        return RedirectResponse(url="/admin/login", status_code=302)

    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return RedirectResponse(url="/admin/login", status_code=302)

    return user
