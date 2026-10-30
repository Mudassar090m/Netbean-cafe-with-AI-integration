"""Pydantic v2 model for a café menu item."""
from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class MenuItem(BaseModel):
    """A single item on the Bright Bean Café menu."""

    id: Annotated[int, Field(gt=0, description="Unique positive integer identifier")]
    name: Annotated[str, Field(min_length=1, max_length=100)]
    category: Annotated[str, Field(min_length=1, max_length=50)]
    description: Annotated[str, Field(max_length=500, default="")]
    price: Annotated[float, Field(ge=0.01, le=9999.99)]
    image: Annotated[str, Field(min_length=1, max_length=2048)]
    featured: bool | None = None
    tags: Annotated[
        list[Annotated[str, Field(max_length=50)]] | None,
        Field(max_length=20, default=None),
    ] = None

    model_config = ConfigDict(from_attributes=True)
