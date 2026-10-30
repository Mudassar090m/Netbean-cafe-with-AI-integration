"""In-memory data stores for menu items and gallery items, with seed logic."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from backend.models.gallery import GalleryItem
from backend.models.menu import MenuItem

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singletons — populated during startup
# ---------------------------------------------------------------------------
_menu_items: dict[int, MenuItem] = {}
_gallery_items: dict[int, GalleryItem] = {}


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------

def seed_menu(path: str) -> None:
    """Read *data/menu.json*, validate every entry, and populate the menu store.

    Raises ``SystemExit(1)`` if the file is missing or contains invalid JSON
    so that the server never starts with an empty or corrupt menu.
    """
    global _menu_items
    json_path = Path(path)

    if not json_path.exists():
        logger.error("menu.json not found at %s — aborting startup", json_path)
        raise SystemExit(1)

    try:
        raw: list[dict] = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        logger.error("menu.json contains invalid JSON: %s — aborting startup", exc)
        raise SystemExit(1)

    new_store: dict[int, MenuItem] = {}
    for entry in raw:
        item = MenuItem.model_validate(entry)
        new_store[item.id] = item

    _menu_items = new_store
    logger.info("Menu store seeded with %d items", len(_menu_items))


def seed_gallery(items: list[dict]) -> None:
    """Populate the gallery store from a list of dicts.

    Idempotent — clears the existing store before refilling it, so calling
    this multiple times with the same data produces the same result.
    """
    global _gallery_items
    _gallery_items = {}
    for entry in items:
        item = GalleryItem.model_validate(entry)
        _gallery_items[item.id] = item
    logger.info("Gallery store seeded with %d items", len(_gallery_items))


# ---------------------------------------------------------------------------
# Query functions
# ---------------------------------------------------------------------------

def get_menu_items(category: str | None = None) -> list[MenuItem]:
    """Return all menu items, or only those matching *category* exactly.

    Passing ``None`` or ``"All"`` returns every item.
    An unrecognised category returns an empty list.
    """
    if category is None or category == "All":
        return list(_menu_items.values())
    return [item for item in _menu_items.values() if item.category == category]


def get_menu_item(item_id: int) -> MenuItem | None:
    """Return the menu item with the given *id*, or ``None`` if not found."""
    return _menu_items.get(item_id)


def get_gallery_items(category: str | None = None) -> list[GalleryItem]:
    """Return all gallery items, or only those matching *category* exactly.

    Passing ``None`` or ``"All"`` returns every item.
    An unrecognised category returns an empty list.
    """
    if category is None or category == "All":
        return list(_gallery_items.values())
    return [item for item in _gallery_items.values() if item.category == category]
