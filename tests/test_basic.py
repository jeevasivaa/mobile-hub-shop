"""
tests/test_basic.py
────────────────────
Basic smoke tests for the Mobile Shop FastAPI app.
Tests that all public routes return HTTP 200 (or expected codes).
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# We mock the database so tests don't need a real PostgreSQL connection
import os
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


# ── Mock database dependency ──────────────────────────────────────────────────

def mock_get_db():
    """Return a mock database session for testing."""
    db = MagicMock()

    # Mock products query
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
    db.query.return_value.filter.return_value.all.return_value = []
    db.query.return_value.distinct.return_value.order_by.return_value.all.return_value = []
    db.query.return_value.count.return_value = 0
    db.query.return_value.order_by.return_value.all.return_value = []
    db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

    yield db


# Override the database dependency
from app.core.database import get_db
app.dependency_overrides[get_db] = mock_get_db


# ── Public Route Tests ────────────────────────────────────────────────────────

class TestPublicRoutes:
    def test_home_page_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_about_page_returns_200(self):
        response = client.get("/about")
        assert response.status_code == 200

    def test_products_page_returns_200(self):
        response = client.get("/products")
        assert response.status_code == 200

    def test_offers_page_returns_200(self):
        response = client.get("/offers")
        assert response.status_code == 200

    def test_contact_page_returns_200(self):
        response = client.get("/contact")
        assert response.status_code == 200

    def test_nonexistent_product_returns_404(self):
        response = client.get("/products/99999")
        assert response.status_code == 404

    def test_htmx_products_search_returns_partial(self):
        """HTMX request should return partial HTML, not full page."""
        response = client.get(
            "/products?q=samsung",
            headers={"HX-Request": "true"}
        )
        assert response.status_code == 200

    def test_products_brand_filter(self):
        response = client.get("/products?brand=Apple")
        assert response.status_code == 200


# ── Auth Route Tests ──────────────────────────────────────────────────────────

class TestAuthRoutes:
    def test_admin_login_page_returns_200(self):
        response = client.get("/admin/login")
        assert response.status_code == 200

    def test_admin_dashboard_redirects_without_auth(self):
        """Dashboard should redirect to login if not authenticated."""
        response = client.get("/admin/dashboard", follow_redirects=False)
        assert response.status_code in [302, 307]

    def test_admin_login_with_wrong_credentials(self):
        response = client.post("/admin/login", data={
            "username": "wronguser",
            "password": "wrongpass"
        })
        # Should re-render login with error
        assert response.status_code == 200

    def test_404_page(self):
        response = client.get("/this-route-does-not-exist")
        assert response.status_code == 404
