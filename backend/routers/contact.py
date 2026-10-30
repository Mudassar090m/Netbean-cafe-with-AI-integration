"""API router for contact form endpoints.

Routes:
  POST /api/contact   — submit a contact message
  GET  /api/contact   — retrieve all submissions (newest first)
"""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import ContactMessageORM
from backend.models.contact import ContactMessage, ContactMessageResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["contact"])


@router.post("/contact", response_model=dict, status_code=201)
def submit_contact(
    body: ContactMessage,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Persist a contact form submission and return a confirmation with the new id."""
    try:
        record = ContactMessageORM(
            name=body.name,
            email=body.email,
            subject=body.subject,
            message=body.message,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database error while saving contact message: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable",
        ) from exc

    return {"message": "Message received", "id": record.id}


@router.get("/contact", response_model=list[ContactMessageResponse])
def list_contacts(
    db: Annotated[Session, Depends(get_db)],
) -> list[ContactMessageORM]:
    """Return all contact submissions ordered by submission time descending."""
    return (
        db.query(ContactMessageORM)
        .order_by(ContactMessageORM.submitted_at.desc())
        .all()
    )
