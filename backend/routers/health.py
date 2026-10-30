"""API router for the health check endpoint.

Routes:
  GET /health   — return service health, probing the database
"""
from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.models.contact import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(
    db: Annotated[Session, Depends(get_db)],
) -> JSONResponse:
    """Return ``{"status": "ok"}`` when the database is reachable.

    Returns HTTP 503 with ``{"status": "degraded"}`` when the database
    probe fails.
    """
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.warning("Health check: database unreachable — %s", exc)
        return JSONResponse(
            status_code=503,
            content=HealthResponse(
                status="degraded",
                service="bright-bean-api",
                detail="Database unreachable",
            ).model_dump(),
        )

    return JSONResponse(
        status_code=200,
        content=HealthResponse(status="ok", service="bright-bean-api").model_dump(),
    )
