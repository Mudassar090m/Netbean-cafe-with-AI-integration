"""API router for order endpoints.

Routes:
  POST /api/orders   — place a new order (saves to SQLite)
  GET  /api/orders   — list all orders (newest first)
  GET  /api/orders/{id} — get a single order by id
"""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import OrderItemORM, OrderORM
from backend.models.order import OrderIn, OrderOut

logger = logging.getLogger(__name__)

router = APIRouter(tags=["orders"])


@router.post("/orders", response_model=OrderOut, status_code=201)
def place_order(
    body: OrderIn,
    db: Annotated[Session, Depends(get_db)],
) -> OrderORM:
    """Persist a new order and return it with its generated id.

    Accepts any number of line items — there is no cap.
    For delivery orders, delivery_address is required.
    """
    total = round(
        sum(item.price * item.quantity for item in body.items), 2
    )

    try:
        order = OrderORM(
            customer_name=body.customer_name,
            customer_email=body.customer_email,
            customer_phone=body.customer_phone,
            order_type=body.order_type,
            delivery_address=body.delivery_address,
            notes=body.notes,
            total=total,
            status="pending",
        )
        db.add(order)
        db.flush()  # populate order.id before inserting items

        for item in body.items:
            db.add(
                OrderItemORM(
                    order_id=order.id,
                    menu_item_id=item.menu_item_id,
                    name=item.name,
                    price=item.price,
                    quantity=item.quantity,
                )
            )

        db.commit()
        db.refresh(order)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database error while saving order: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable",
        ) from exc

    return order


@router.get("/orders", response_model=list[OrderOut])
def list_orders(
    db: Annotated[Session, Depends(get_db)],
) -> list[OrderORM]:
    """Return all orders, newest first."""
    return (
        db.query(OrderORM)
        .order_by(OrderORM.placed_at.desc())
        .all()
    )


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> OrderORM:
    """Return a single order by id."""
    order = db.get(OrderORM, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order
