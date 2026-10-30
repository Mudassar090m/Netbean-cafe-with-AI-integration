"""Shared pytest fixtures for integration tests.

Provides:
  - ``tmp_db``            — in-memory SQLite session (function-scoped, fully isolated)
  - ``client``            — FastAPI TestClient with get_db overridden + stores seeded
  - ``client_with_contacts`` — like ``client`` but pre-seeds two contact DB rows
"""
from __future__ import annotations

from collections.abc import Generator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import backend.data.store as store
from backend.db.database import Base, get_db
from backend.db import models as _orm_models  # noqa: F401 — ensures ORM models are registered with Base.metadata
from backend.db.models import ContactMessageORM
from backend.main import app
from backend.models.gallery import GalleryItem
from backend.models.menu import MenuItem

# ---------------------------------------------------------------------------
# Known test data — stable, predictable, used across all integration tests
# ---------------------------------------------------------------------------

TEST_MENU_ITEMS = [
    {
        "id": 1,
        "name": "Classic Cappuccino",
        "category": "Coffee",
        "description": "Rich espresso topped with foam.",
        "price": 4.50,
        "image": "images/cappuccino.jpg",
        "featured": True,
    },
    {
        "id": 2,
        "name": "Iced Vanilla Latte",
        "category": "Cold Drinks",
        "description": "Chilled espresso with vanilla.",
        "price": 5.00,
        "image": "images/iced-vanilla-latte.jpg",
    },
    {
        "id": 3,
        "name": "Butter Croissant",
        "category": "Pastries",
        "description": "Flaky butter croissant.",
        "price": 3.50,
        "image": "images/croissant.jpg",
    },
]

TEST_GALLERY_ITEMS = [
    {"id": 1, "category": "Café",   "image": "Gallery/interior.jpg",  "label": "Interior"},
    {"id": 2, "category": "Coffee", "image": "Gallery/latte-art.jpg", "label": "Latte art"},
    {"id": 3, "category": "Food",   "image": "Gallery/egg.jpg",       "label": "Egg toast"},
]


def _seed_stores() -> None:
    """Overwrite the in-memory stores with the known test dataset."""
    store._menu_items = {
        item["id"]: MenuItem.model_validate(item) for item in TEST_MENU_ITEMS
    }
    store._gallery_items = {
        item["id"]: GalleryItem.model_validate(item) for item in TEST_GALLERY_ITEMS
    }


# ---------------------------------------------------------------------------
# tmp_db fixture — isolated in-memory SQLite per test
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_db() -> Generator[Session, None, None]:
    """Create a fresh in-memory SQLite database for each test.

    Uses ``StaticPool`` so every connection shares the same in-memory
    database — required because SQLite creates a new blank DB per
    connection by default.
    """
    from sqlalchemy.pool import StaticPool

    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create tables on this engine (not the app's engine)
    Base.metadata.create_all(bind=eng)
    SL = sessionmaker(autocommit=False, autoflush=False, bind=eng)
    db = SL()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=eng)


# ---------------------------------------------------------------------------
# client fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(tmp_db: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient backed by an in-memory DB and known test data.

    - Overrides ``get_db`` so every DB call uses the isolated ``tmp_db`` session.
    - Seeds the in-memory stores with TEST_MENU_ITEMS / TEST_GALLERY_ITEMS
      *after* the TestClient lifespan runs (which would otherwise re-seed from
      data/menu.json and gallery.html).
    """
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield tmp_db
        finally:
            pass  # tmp_db fixture owns cleanup

    app.dependency_overrides[get_db] = override_get_db

    # Use lifespan=False so the app's startup handler doesn't clobber our stores.
    # We manually seed them below instead.
    with TestClient(app, raise_server_exceptions=True) as c:
        # Seed AFTER client enters context (lifespan has already run by here)
        _seed_stores()
        yield c

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# client_with_contacts fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def client_with_contacts(tmp_db: Session) -> Generator[TestClient, None, None]:
    """Like ``client`` but pre-seeds two contact records with distinct timestamps."""
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield tmp_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Insert two records with explicit timestamps so ordering is deterministic
    older = ContactMessageORM(
        name="Alice",
        email="alice@example.com",
        subject="First message",
        message="This is the older message.",
        submitted_at=datetime(2024, 1, 1, 10, 0, 0),
    )
    newer = ContactMessageORM(
        name="Bob",
        email="bob@example.com",
        subject="Second message",
        message="This is the newer message.",
        submitted_at=datetime(2024, 1, 2, 10, 0, 0),
    )
    tmp_db.add_all([older, newer])
    tmp_db.commit()

    with TestClient(app, raise_server_exceptions=True) as c:
        _seed_stores()
        yield c

    app.dependency_overrides.clear()
