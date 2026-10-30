"""Property-based HTTP-layer tests (tasks 9.1 – 9.6).

Each test function maps to a named property from the design document.
All Hypothesis tests run a minimum of 100 examples.

Properties covered:
  3 — Single item lookup round-trip
  4 — Contact submission round-trip
  5 — Contact submission ordering invariant
  6 — Whitespace-only fields are rejected
  7 — Invalid email addresses are rejected
  10 — Error responses always carry Content-Type: application/json
"""
from __future__ import annotations

import re
from collections.abc import Generator
from datetime import datetime

from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import backend.data.store as store
from backend.db.database import Base, get_db
from backend.main import app
from backend.models.gallery import GalleryItem
from backend.models.menu import MenuItem


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

def _non_whitespace_text(min_size: int = 2, max_size: int = 100) -> st.SearchStrategy[str]:
    return st.text(
        alphabet=st.characters(blacklist_categories=("Cs",)),
        min_size=min_size,
        max_size=max_size,
    ).filter(lambda s: s.strip() and len(s.strip()) >= 1)


def contact_message_strategy() -> st.SearchStrategy[dict]:
    return st.fixed_dictionaries(
        {
            "name": _non_whitespace_text(2, 100),
            "email": st.emails(),
            "subject": _non_whitespace_text(2, 150),
            "message": _non_whitespace_text(6, 500),
        }
    )


def menu_item_strategy() -> st.SearchStrategy[dict]:
    return st.fixed_dictionaries(
        {
            "id": st.integers(min_value=100, max_value=99_999),
            "name": st.text(min_size=1, max_size=50).filter(str.strip),
            "category": st.sampled_from(["Coffee", "Cold Drinks", "Pastries", "Tea"]),
            "description": st.text(max_size=100),
            "price": st.floats(
                min_value=0.01, max_value=999.99, allow_nan=False, allow_infinity=False
            ),
            "image": st.text(min_size=1, max_size=100).filter(str.strip),
        }
    )


# ---------------------------------------------------------------------------
# Per-test DB + client helpers
# ---------------------------------------------------------------------------

def _fresh_db() -> tuple[Session, object]:
    """Return a (session, engine) pair backed by a brand-new in-memory SQLite DB.

    Uses ``StaticPool`` so every connection shares the same in-memory database.
    """
    from sqlalchemy.pool import StaticPool

    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=eng)
    SL = sessionmaker(autocommit=False, autoflush=False, bind=eng)
    return SL(), eng


def _make_client(db: Session) -> TestClient:
    """Return a TestClient that uses *db* for all DB operations."""
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app, raise_server_exceptions=True)


def _teardown(db: Session, eng) -> None:
    db.close()
    Base.metadata.drop_all(bind=eng)
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Property 3: Single item lookup round-trip
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(item=menu_item_strategy())
def test_single_item_lookup_roundtrip(item: dict) -> None:
    """Property 3 — GET /api/menu/{id} returns a body value-equal to the seeded item."""
    db, eng = _fresh_db()
    try:
        with _make_client(db) as client:
            # Seed stores AFTER lifespan runs
            store._menu_items = {item["id"]: MenuItem.model_validate(item)}
            store._gallery_items = {}

            resp = client.get(f"/api/menu/{item['id']}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == item["id"]
        assert body["name"] == item["name"]
        assert body["category"] == item["category"]
        assert abs(body["price"] - item["price"]) < 0.001
    finally:
        _teardown(db, eng)


# ---------------------------------------------------------------------------
# Property 4: Contact submission round-trip
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(msg=contact_message_strategy())
def test_contact_submission_roundtrip(msg: dict) -> None:
    """Property 4 — a valid submission appears in GET /api/contact after POST."""
    db, eng = _fresh_db()
    try:
        with _make_client(db) as client:
            store._menu_items = {}
            store._gallery_items = {}

            post_resp = client.post("/api/contact", json=msg)
            assert post_resp.status_code == 201
            submitted_id = post_resp.json()["id"]

            get_resp = client.get("/api/contact")
            assert get_resp.status_code == 200
            contacts = get_resp.json()

        # Find the record by the id returned in the POST response.
        # We don't compare email directly because Pydantic's EmailStr may
        # normalise the domain via IDNA encoding.
        match = next((c for c in contacts if c["id"] == submitted_id), None)
        assert match is not None, f"Contact id={submitted_id} not found in GET response"
        assert match["name"] == msg["name"]
        assert match["subject"] == msg["subject"]
        assert match["message"] == msg["message"]
        assert isinstance(match["email"], str) and len(match["email"]) > 0
    finally:
        _teardown(db, eng)


# ---------------------------------------------------------------------------
# Property 5: Contact submission ordering invariant
# ---------------------------------------------------------------------------

@settings(max_examples=50)
@given(msgs=st.lists(contact_message_strategy(), min_size=2, max_size=6))
def test_contact_ordering_invariant(msgs: list[dict]) -> None:
    """Property 5 — GET /api/contact always returns submissions newest-first."""
    db, eng = _fresh_db()
    try:
        with _make_client(db) as client:
            store._menu_items = {}
            store._gallery_items = {}

            for msg in msgs:
                resp = client.post("/api/contact", json=msg)
                assert resp.status_code == 201

            contacts = client.get("/api/contact").json()

        timestamps = []
        for c in contacts:
            ts_str = c["submitted_at"]
            if ts_str.endswith("Z"):
                ts_str = ts_str[:-1] + "+00:00"
            timestamps.append(datetime.fromisoformat(ts_str))

        for i in range(len(timestamps) - 1):
            assert timestamps[i] >= timestamps[i + 1], (
                f"Contact at index {i} ({timestamps[i]}) is older than "
                f"contact at index {i+1} ({timestamps[i+1]})"
            )
    finally:
        _teardown(db, eng)


# ---------------------------------------------------------------------------
# Property 6: Whitespace-only fields are rejected
# ---------------------------------------------------------------------------

_WHITESPACE = st.text(alphabet=" \t\n\r", min_size=0, max_size=50)
_WHITESPACE_FIELDS = st.sampled_from(["name", "subject", "message"])

VALID_BASE = {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "subject": "Hello there",
    "message": "This is a valid message body.",
}


@settings(max_examples=100)
@given(whitespace=_WHITESPACE, field=_WHITESPACE_FIELDS)
def test_whitespace_only_fields_rejected(whitespace: str, field: str) -> None:
    """Property 6 — whitespace-only value for name/subject/message yields 422."""
    db, eng = _fresh_db()
    try:
        with _make_client(db) as client:
            store._menu_items = {}
            store._gallery_items = {}

            before = len(client.get("/api/contact").json())
            payload = {**VALID_BASE, field: whitespace}
            resp = client.post("/api/contact", json=payload)
            after = len(client.get("/api/contact").json())

        assert resp.status_code == 422
        assert before == after, "Contact count changed despite rejected submission"
    finally:
        _teardown(db, eng)


# ---------------------------------------------------------------------------
# Property 7: Invalid email addresses are rejected
# ---------------------------------------------------------------------------

def _is_plausibly_valid_email(s: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", s))


@settings(max_examples=100)
@given(
    bad_email=st.text(min_size=1, max_size=100).filter(
        lambda s: not _is_plausibly_valid_email(s)
    )
)
def test_invalid_email_rejected(bad_email: str) -> None:
    """Property 7 — any string that isn't a valid email yields 422."""
    db, eng = _fresh_db()
    try:
        with _make_client(db) as client:
            store._menu_items = {}
            store._gallery_items = {}
            payload = {**VALID_BASE, "email": bad_email}
            resp = client.post("/api/contact", json=payload)
        assert resp.status_code == 422
    finally:
        _teardown(db, eng)


# ---------------------------------------------------------------------------
# Property 10: Error responses carry Content-Type: application/json
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(bad_id=st.integers().filter(lambda x: x <= 0))
def test_error_responses_have_json_content_type_menu(bad_id: int) -> None:
    """Property 10 (menu 422) — error response has Content-Type: application/json."""
    db, eng = _fresh_db()
    try:
        with _make_client(db) as client:
            store._menu_items = {}
            store._gallery_items = {}
            resp = client.get(f"/api/menu/{bad_id}")
        assert resp.status_code == 422
        assert "application/json" in resp.headers["content-type"]
        assert "detail" in resp.json()
    finally:
        _teardown(db, eng)


@settings(max_examples=50)
@given(whitespace=_WHITESPACE, field=_WHITESPACE_FIELDS)
def test_error_responses_have_json_content_type_contact(
    whitespace: str, field: str
) -> None:
    """Property 10 (contact 422) — error response has Content-Type: application/json."""
    db, eng = _fresh_db()
    try:
        with _make_client(db) as client:
            store._menu_items = {}
            store._gallery_items = {}
            payload = {**VALID_BASE, field: whitespace}
            resp = client.post("/api/contact", json=payload)
        assert resp.status_code == 422
        assert "application/json" in resp.headers["content-type"]
        assert "detail" in resp.json()
    finally:
        _teardown(db, eng)
