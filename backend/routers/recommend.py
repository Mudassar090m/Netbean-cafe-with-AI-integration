"""API router for menu item recommendations (scikit-learn TF-IDF)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.data import store
from backend.models.menu import MenuItem
from backend.services.recommender import recommend, recommend_cart

router = APIRouter(tags=["recommend"])


class CartRecommendIn(BaseModel):
    item_ids: list[int] = Field(min_length=1)


@router.get("/recommend/{item_id}", response_model=list[MenuItem])
def get_similar(
    item_id: int,
    limit: Annotated[int, Query(gt=0, le=10)] = 3,
) -> list[MenuItem]:
    """Return menu items most similar to *item_id*."""
    if store.get_menu_item(item_id) is None:
        raise HTTPException(status_code=404, detail=f"Menu item {item_id} not found")
    return recommend(item_id, limit=limit)


@router.post("/recommend/cart", response_model=list[MenuItem])
def recommend_for_cart(body: CartRecommendIn) -> list[MenuItem]:
    """Return items most similar to the provided cart item ids."""
    invalid = [i for i in body.item_ids if store.get_menu_item(i) is None]
    if invalid:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown item ids: {invalid}",
        )
    return recommend_cart(body.item_ids)
