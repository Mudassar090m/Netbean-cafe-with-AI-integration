"""Pydantic v2 models for order placement and retrieval."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrderItemIn(BaseModel):
    """A single line item sent by the browser when placing an order."""

    menu_item_id: Annotated[int, Field(gt=0)]
    name: Annotated[str, Field(min_length=1, max_length=100)]
    price: Annotated[float, Field(gt=0)]
    quantity: Annotated[int, Field(gt=0, le=99)]


class OrderIn(BaseModel):
    """Request body for POST /api/orders.

    order_type:
      'pickup'   — customer collects in person (no address required)
      'delivery' — café delivers; delivery_address is required
    """

    customer_name: Annotated[str, Field(min_length=2, max_length=100)]
    customer_email: Annotated[EmailStr, Field(max_length=254)]
    customer_phone: Annotated[str | None, Field(max_length=30, default=None)] = None
    order_type: Literal["pickup", "delivery"] = "pickup"
    delivery_address: Annotated[str | None, Field(max_length=500, default=None)] = None
    notes: Annotated[str | None, Field(max_length=500, default=None)] = None
    # No upper limit on items — customers can order the full menu
    items: Annotated[list[OrderItemIn], Field(min_length=1)]

    def model_post_init(self, __context) -> None:  # noqa: ANN001
        """Enforce address is provided for delivery orders."""
        if self.order_type == "delivery" and not (self.delivery_address or "").strip():
            raise ValueError("delivery_address is required for delivery orders")


class OrderItemOut(BaseModel):
    """A single line item returned in an order response."""

    id: int
    menu_item_id: int
    name: str
    price: float
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class OrderOut(BaseModel):
    """Full order record returned from GET /api/orders or POST /api/orders."""

    id: int
    customer_name: str
    customer_email: str
    customer_phone: str | None
    order_type: str
    delivery_address: str | None
    notes: str | None
    total: float
    status: str
    placed_at: datetime
    items: list[OrderItemOut]

    model_config = ConfigDict(from_attributes=True)
