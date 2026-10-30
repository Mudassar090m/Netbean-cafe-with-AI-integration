"""Integration tests for all HTTP endpoints (tasks 8.2 – 8.5).

Uses the ``client`` and ``client_with_contacts`` fixtures from conftest.py.
Each test exercises the full FastAPI request/response cycle against an
in-memory SQLite database and pre-seeded in-memory stores.
"""
from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient


# ===========================================================================
# 8.2  Menu endpoints
# ===========================================================================

class TestMenuList:
    def test_returns_all_items(self, client: TestClient) -> None:
        resp = client.get("/api/menu")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

    def test_content_type_is_json(self, client: TestClient) -> None:
        resp = client.get("/api/menu")
        assert "application/json" in resp.headers["content-type"]

    def test_category_all_returns_all(self, client: TestClient) -> None:
        resp = client.get("/api/menu?category=All")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_category_filter_coffee(self, client: TestClient) -> None:
        resp = client.get("/api/menu?category=Coffee")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["name"] == "Classic Cappuccino"

    def test_category_filter_nonexistent_returns_empty(self, client: TestClient) -> None:
        resp = client.get("/api/menu?category=Nonexistent")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_item_shape(self, client: TestClient) -> None:
        """Every returned item must have the required fields."""
        resp = client.get("/api/menu")
        for item in resp.json():
            for field in ("id", "name", "category", "description", "price", "image"):
                assert field in item


class TestMenuDetail:
    def test_returns_correct_item(self, client: TestClient) -> None:
        resp = client.get("/api/menu/1")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Classic Cappuccino"

    def test_nonexistent_id_returns_404(self, client: TestClient) -> None:
        resp = client.get("/api/menu/9999")
        assert resp.status_code == 404
        assert "detail" in resp.json()

    def test_zero_id_returns_422(self, client: TestClient) -> None:
        resp = client.get("/api/menu/0")
        assert resp.status_code == 422

    def test_negative_id_returns_422(self, client: TestClient) -> None:
        resp = client.get("/api/menu/-1")
        assert resp.status_code == 422

    def test_string_id_returns_422(self, client: TestClient) -> None:
        resp = client.get("/api/menu/abc")
        assert resp.status_code == 422

    def test_404_response_has_detail(self, client: TestClient) -> None:
        resp = client.get("/api/menu/9999")
        body = resp.json()
        assert "detail" in body
        assert isinstance(body["detail"], str)


# ===========================================================================
# 8.3  Contact endpoints
# ===========================================================================

VALID_CONTACT = {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "subject": "Table booking",
    "message": "Hello, I would like to book a table for two.",
}


class TestContactSubmit:
    def test_valid_submission_returns_201(self, client: TestClient) -> None:
        resp = client.post("/api/contact", json=VALID_CONTACT)
        assert resp.status_code == 201

    def test_response_contains_message_and_id(self, client: TestClient) -> None:
        resp = client.post("/api/contact", json=VALID_CONTACT)
        body = resp.json()
        assert "message" in body
        assert "id" in body
        assert isinstance(body["id"], int)

    def test_whitespace_only_name_returns_422(self, client: TestClient) -> None:
        payload = {**VALID_CONTACT, "name": "   "}
        resp = client.post("/api/contact", json=payload)
        assert resp.status_code == 422

    def test_whitespace_only_subject_returns_422(self, client: TestClient) -> None:
        payload = {**VALID_CONTACT, "subject": "\t\n"}
        resp = client.post("/api/contact", json=payload)
        assert resp.status_code == 422

    def test_whitespace_only_message_returns_422(self, client: TestClient) -> None:
        payload = {**VALID_CONTACT, "message": "     "}
        resp = client.post("/api/contact", json=payload)
        assert resp.status_code == 422

    def test_invalid_email_returns_422(self, client: TestClient) -> None:
        payload = {**VALID_CONTACT, "email": "not-an-email"}
        resp = client.post("/api/contact", json=payload)
        assert resp.status_code == 422

    def test_malformed_json_returns_400(self, client: TestClient) -> None:
        resp = client.post(
            "/api/contact",
            content=b"{ this is not json }",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        assert "detail" in resp.json()

    def test_missing_required_field_returns_422(self, client: TestClient) -> None:
        payload = {k: v for k, v in VALID_CONTACT.items() if k != "email"}
        resp = client.post("/api/contact", json=payload)
        assert resp.status_code == 422


class TestContactList:
    def test_returns_200(self, client: TestClient) -> None:
        resp = client.get("/api/contact")
        assert resp.status_code == 200

    def test_returns_list(self, client: TestClient) -> None:
        assert isinstance(client.get("/api/contact").json(), list)

    def test_submitted_message_appears_in_list(self, client: TestClient) -> None:
        client.post("/api/contact", json=VALID_CONTACT)
        contacts = client.get("/api/contact").json()
        assert any(c["name"] == "Jane Smith" for c in contacts)

    def test_ordered_newest_first(self, client_with_contacts: TestClient) -> None:
        """Pre-seeded contacts: Bob (newer) and Alice (older) — Bob must come first."""
        contacts = client_with_contacts.get("/api/contact").json()
        assert len(contacts) == 2
        assert contacts[0]["name"] == "Bob"
        assert contacts[1]["name"] == "Alice"


# ===========================================================================
# 8.4  Gallery and health endpoints
# ===========================================================================

class TestGallery:
    def test_returns_all_items(self, client: TestClient) -> None:
        resp = client.get("/api/gallery")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_category_all_returns_all(self, client: TestClient) -> None:
        resp = client.get("/api/gallery?category=All")
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_category_filter(self, client: TestClient) -> None:
        resp = client.get("/api/gallery?category=Coffee")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["label"] == "Latte art"

    def test_nonexistent_category_returns_empty(self, client: TestClient) -> None:
        resp = client.get("/api/gallery?category=Nonexistent")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_item_shape(self, client: TestClient) -> None:
        for item in client.get("/api/gallery").json():
            for field in ("id", "category", "image", "label"):
                assert field in item


class TestHealth:
    def test_returns_200_when_healthy(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_status_is_ok(self, client: TestClient) -> None:
        body = client.get("/health").json()
        assert body["status"] == "ok"

    def test_service_name(self, client: TestClient) -> None:
        body = client.get("/health").json()
        assert body["service"] == "bright-bean-api"

    def test_degraded_when_db_fails(self, client: TestClient) -> None:
        """Override get_db to raise OperationalError to simulate a DB failure."""
        from unittest.mock import MagicMock
        from sqlalchemy.exc import OperationalError
        from sqlalchemy.orm import Session
        from backend.db.database import get_db

        # Create a mock session whose execute() raises OperationalError
        mock_db = MagicMock(spec=Session)
        mock_db.execute.side_effect = OperationalError(
            "simulated db failure", None, Exception("db down")
        )

        def broken_db() -> Generator:
            yield mock_db

        from backend.main import app as _app
        _app.dependency_overrides[get_db] = broken_db
        try:
            resp = client.get("/health")
            assert resp.status_code == 503
            assert resp.json()["status"] == "degraded"
        finally:
            # Re-apply the fixture's own override
            def restore_db() -> Generator:
                try:
                    yield client.__dict__.get("_db_override") or mock_db
                finally:
                    pass
            del _app.dependency_overrides[get_db]


class TestCORS:
    def test_preflight_returns_200(self, client: TestClient) -> None:
        resp = client.options(
            "/api/menu",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        # FastAPI's CORSMiddleware returns 200 for preflight
        assert resp.status_code == 200

    def test_cors_header_present_on_get(self, client: TestClient) -> None:
        resp = client.get("/api/menu", headers={"Origin": "http://localhost"})
        assert "access-control-allow-origin" in resp.headers


# ===========================================================================
# 8.5  Static file serving
# ===========================================================================

class TestStaticFiles:
    def test_index_html_returns_200(self, client: TestClient) -> None:
        resp = client.get("/index.html")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]

    def test_nonexistent_static_file_returns_404(self, client: TestClient) -> None:
        resp = client.get("/this-file-does-not-exist-abc123.html")
        assert resp.status_code == 404

    def test_undefined_api_route_returns_404(self, client: TestClient) -> None:
        """An unknown /api/* path must return JSON 404, not a static file."""
        resp = client.get("/api/nonexistent-endpoint")
        assert resp.status_code == 404
