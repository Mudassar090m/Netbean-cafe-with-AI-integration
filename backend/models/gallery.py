"""Pydantic v2 model for a gallery image item."""
from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class GalleryItem(BaseModel):
    """A single photo entry in the Bright Bean Café gallery."""

    id: Annotated[int, Field(gt=0, description="Unique positive integer identifier")]
    category: Annotated[str, Field(min_length=1)]
    image: Annotated[str, Field(min_length=1, description="Relative URL path to the image file")]
    label: Annotated[str, Field(min_length=1)]
