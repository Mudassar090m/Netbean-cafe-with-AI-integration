"""Unit and property-based tests for backend/data/store.py.

Covers:
  - Property 1: Category filter completeness — menu
  - Property 2: MenuItem schema completeness
  - Property 8: Category filter completeness — gallery
  - Property 9: GalleryItem schema completeness
  - Unit: seed_menu raises SystemExit on missing / malformed JSON
  - Unit: seed_gallery idempotency
  - Unit: get_menu_items("All") and get_menu_items(None) return everything
  - Unit: get_menu_item returns None for unknown id
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import backend.data.store as store
from backend.models.gallery import GalleryItem
from backend.models.menu import MenuItem

# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

_CATEGORIES = ["Coffee", "Cold Drinks", "Pastries", "Desserts", "Tea", "Other"]


def menu_item_strategy():
    return st.fixed_dictionaries(
        {
            "id": st.integers(min_value=1, max_value=10_000),
            "name": st.text(min_size=1, max_size=100).filter(lambda s: s.strip()),
            "category": st.one_of(
                st.sampled_from(_CATEGORIES),
                st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
            ),
            "description": st.text(max_size=500),
            "price": st.floats(min_value=0.01, max_value=9999.99, allow_nan=False, allow_infinity=False),
            "image": st.text(min_size=1, max_size=200).filter(lambda s: s.strip()),
        }
    )


def gallery_item_strategy():
    return st.fixed_dictionaries(
        {
            "id": st.integers(min_value=1, max_value=10_000),
            "category": st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
            "image": st.text(min_size=1, max_size=200).filter(lambda s: s.strip()),
            "label": st.text(min_size=1, max_size=200).filter(lambda s: s.strip()),
        }
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_menu_store(items: list[dict]) -> None:
    """Directly populate the in-memory menu store for testing."""
    store._menu_items = {
        item["id"]: MenuItem.model_validate(item)
        for item in items
    }


def _load_gallery_store(items: list[dict]) -> None:
    """Directly populate the in-memory gallery store for testing."""
    store._gallery_items = {
        item["id"]: GalleryItem.model_validate(item)
        for item in items
    }


# ---------------------------------------------------------------------------
# Property 1: Category filter completeness — menu
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    items=st.lists(menu_item_strategy(), min_size=1, max_size=30),
    # Exclude the sentinel value "All" which has special pass-through semantics
    category=st.text(min_size=1, max_size=50).filter(
        lambda s: s.strip() and s != "All"
    ),
)
def test_menu_category_filter_completeness(items: list[dict], category: str) -> None:
    """Property 1 — GET /api/menu?category=C returns exactly the items whose
    category equals C (case-sensitive), no more and no fewer.
    The sentinel value "All" is excluded — it is covered by a dedicated unit test."""
    # Deduplicate ids to avoid dict collision
    seen_ids: set[int] = set()
    unique_items = []
    for item in items:
        if item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            unique_items.append(item)

    _load_menu_store(unique_items)
    result = store.get_menu_items(category)
    expected = [i for i in unique_items if i["category"] == category]

    assert len(result) == len(expected)
    result_ids = {r.id for r in result}
    expected_ids = {e["id"] for e in expected}
    assert result_ids == expected_ids


# ---------------------------------------------------------------------------
# Property 2: MenuItem schema completeness
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(items=st.lists(menu_item_strategy(), min_size=1, max_size=20))
def test_menu_item_schema_completeness(items: list[dict]) -> None:
    """Property 2 — every item returned by get_menu_items(None) has all
    required fields present, correctly typed, and within constraints."""
    seen_ids: set[int] = set()
    unique_items = []
    for item in items:
        if item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            unique_items.append(item)

    _load_menu_store(unique_items)
    result = store.get_menu_items(None)

    for item in result:
        assert isinstance(item.id, int) and item.id > 0
        assert isinstance(item.name, str) and 1 <= len(item.name) <= 100
        assert isinstance(item.category, str) and 1 <= len(item.category) <= 50
        assert isinstance(item.description, str) and len(item.description) <= 500
        assert isinstance(item.price, float) and 0.01 <= item.price <= 9999.99
        assert isinstance(item.image, str) and len(item.image) >= 1


# ---------------------------------------------------------------------------
# Property 8: Category filter completeness — gallery
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    items=st.lists(gallery_item_strategy(), min_size=1, max_size=20),
    # Exclude the sentinel value "All" which has special pass-through semantics
    category=st.text(min_size=1, max_size=50).filter(
        lambda s: s.strip() and s != "All"
    ),
)
def test_gallery_category_filter_completeness(items: list[dict], category: str) -> None:
    """Property 8 — get_gallery_items(C) returns exactly the items whose
    category equals C (case-sensitive), no more and no fewer.
    The sentinel value "All" is excluded — it is covered by a dedicated unit test."""
    seen_ids: set[int] = set()
    unique_items = []
    for item in items:
        if item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            unique_items.append(item)

    _load_gallery_store(unique_items)
    result = store.get_gallery_items(category)
    expected = [i for i in unique_items if i["category"] == category]

    assert len(result) == len(expected)
    result_ids = {r.id for r in result}
    expected_ids = {e["id"] for e in expected}
    assert result_ids == expected_ids


# ---------------------------------------------------------------------------
# Property 9: GalleryItem schema completeness
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(items=st.lists(gallery_item_strategy(), min_size=1, max_size=20))
def test_gallery_item_schema_completeness(items: list[dict]) -> None:
    """Property 9 — every item returned by get_gallery_items(None) has all
    required fields present and non-empty."""
    seen_ids: set[int] = set()
    unique_items = []
    for item in items:
        if item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            unique_items.append(item)

    _load_gallery_store(unique_items)
    result = store.get_gallery_items(None)

    for item in result:
        assert isinstance(item.id, int) and item.id > 0
        assert isinstance(item.category, str) and len(item.category) >= 1
        assert isinstance(item.image, str) and len(item.image) >= 1
        assert isinstance(item.label, str) and len(item.label) >= 1


# ---------------------------------------------------------------------------
# Unit: seed_menu failure modes
# ---------------------------------------------------------------------------

def test_seed_menu_raises_on_missing_file(tmp_path: Path) -> None:
    """seed_menu should raise SystemExit(1) when the JSON file doesn't exist."""
    with pytest.raises(SystemExit) as exc_info:
        store.seed_menu(str(tmp_path / "nonexistent.json"))
    assert exc_info.value.code == 1


def test_seed_menu_raises_on_invalid_json(tmp_path: Path) -> None:
    """seed_menu should raise SystemExit(1) when the JSON file is malformed."""
    bad_file = tmp_path / "menu.json"
    bad_file.write_text("{ this is not valid json }", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        store.seed_menu(str(bad_file))
    assert exc_info.value.code == 1


def test_seed_menu_loads_valid_file(tmp_path: Path) -> None:
    """seed_menu should populate the store from a valid JSON file."""
    menu_data = [
        {
            "id": 1,
            "name": "Espresso",
            "category": "Coffee",
            "description": "Strong shot",
            "price": 2.5,
            "image": "images/espresso.jpg",
        }
    ]
    menu_file = tmp_path / "menu.json"
    menu_file.write_text(json.dumps(menu_data), encoding="utf-8")

    store.seed_menu(str(menu_file))
    result = store.get_menu_items(None)
    assert len(result) == 1
    assert result[0].name == "Espresso"


# ---------------------------------------------------------------------------
# Unit: seed_gallery idempotency
# ---------------------------------------------------------------------------

def test_seed_gallery_idempotency() -> None:
    """Calling seed_gallery twice with the same data should not create duplicates."""
    items = [
        {"id": 1, "category": "Café", "image": "Gallery/a.jpg", "label": "A"},
        {"id": 2, "category": "Coffee", "image": "Gallery/b.jpg", "label": "B"},
    ]
    store.seed_gallery(items)
    count_first = len(store.get_gallery_items(None))
    store.seed_gallery(items)
    count_second = len(store.get_gallery_items(None))
    assert count_first == count_second == 2


# ---------------------------------------------------------------------------
# Unit: get_menu_items "All" and None semantics
# ---------------------------------------------------------------------------

def test_get_menu_items_none_returns_all() -> None:
    items = [
        {"id": 1, "name": "A", "category": "Coffee", "description": "", "price": 1.0, "image": "a.jpg"},
        {"id": 2, "name": "B", "category": "Tea", "description": "", "price": 2.0, "image": "b.jpg"},
    ]
    _load_menu_store(items)
    assert len(store.get_menu_items(None)) == 2


def test_get_menu_items_all_returns_all() -> None:
    items = [
        {"id": 1, "name": "A", "category": "Coffee", "description": "", "price": 1.0, "image": "a.jpg"},
        {"id": 2, "name": "B", "category": "Tea", "description": "", "price": 2.0, "image": "b.jpg"},
    ]
    _load_menu_store(items)
    assert len(store.get_menu_items("All")) == 2


def test_get_menu_items_unknown_category_returns_empty() -> None:
    items = [
        {"id": 1, "name": "A", "category": "Coffee", "description": "", "price": 1.0, "image": "a.jpg"},
    ]
    _load_menu_store(items)
    assert store.get_menu_items("Nonexistent") == []


# ---------------------------------------------------------------------------
# Unit: get_menu_item
# ---------------------------------------------------------------------------

def test_get_menu_item_returns_none_for_unknown_id() -> None:
    _load_menu_store([])
    assert store.get_menu_item(9999) is None


def test_get_menu_item_returns_correct_item() -> None:
    items = [
        {"id": 42, "name": "Latte", "category": "Coffee", "description": "", "price": 4.0, "image": "latte.jpg"},
    ]
    _load_menu_store(items)
    result = store.get_menu_item(42)
    assert result is not None
    assert result.name == "Latte"
