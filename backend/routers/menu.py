"""API router for menu endpoints.

Routes:
  GET /api/menu          — list all items, optionally filtered by category
  GET /api/menu/{id}     — retrieve a single item by id
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

from backend.data import store
from backend.models.menu import MenuItem

router = APIRouter(tags=["menu"])


@router.get("/menu", response_model=list[MenuItem])
def list_menu_items(
    category: Annotated[
        str | None,
        Query(description="Filter items by category. Omit or pass 'All' for every item."),
    ] = None,
) -> list[MenuItem]:
    """Return all menu items, optionally filtered by *category*."""
    return store.get_menu_items(category)


@router.get("/menu/{item_id}", response_model=MenuItem)
def get_menu_item(
    item_id: Annotated[int, Path(gt=0, description="Unique positive integer id of the menu item")],
) -> MenuItem:
    """Return a single menu item by *item_id*.

    Raises 404 when no item with the given id exists.
    FastAPI automatically returns 422 for non-positive or non-integer ids.
    """
    item = store.get_menu_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Menu item {item_id} not found")
    return item
