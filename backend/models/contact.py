"""Pydantic v2 models for contact form submissions and shared API responses."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ContactMessage(BaseModel):
    """Incoming contact form submission body."""

    name: Annotated[str, Field(min_length=2, max_length=100)]
    email: Annotated[EmailStr, Field(max_length=254)]
    subject: Annotated[str, Field(min_length=2, max_length=150)]
    message: Annotated[str, Field(min_length=6, max_length=2000)]

    @field_validator("name", "subject", "message")
    @classmethod
    def strip_and_reject_whitespace_only(cls, v: str) -> str:
        """Reject strings that consist entirely of whitespace."""
        if not v.strip():
            raise ValueError("Field must contain at least one non-whitespace character")
        return v


class ContactMessageResponse(BaseModel):
    """Outgoing contact message record returned from GET /api/contact."""

    id: int
    name: str
    email: str
    subject: str
    message: str
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Consistent error response shape for all API error responses."""

    detail: str


class HealthResponse(BaseModel):
    """Health check response body."""

    status: Literal["ok", "degraded"]
    service: str
    detail: str | None = None
