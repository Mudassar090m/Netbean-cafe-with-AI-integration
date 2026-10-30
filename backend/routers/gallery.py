"""API router for gallery endpoints.

Routes:
  GET /api/gallery   — list all gallery items, optionally filtered by category
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from backend.data import store
from backend.models.gallery import GalleryItem

router = APIRouter(tags=["gallery"])


@router.get("/gallery", response_model=list[GalleryItem])
def list_gallery_items(
    category: Annotated[
        str | None,
        Query(description="Filter items by category. Omit or pass 'All' for every item."),
    ] = None,
) -> list[GalleryItem]:
    """Return all gallery items, optionally filtered by *category*."""
    return store.get_gallery_items(category)
