"""Core validation schamas."""
from __future__ import annotations

from project_typing import cat_elements

from pydantic import BaseModel


class RequestDataScheme(BaseModel):
    """RequestData  validation scheme."""

    elements: cat_elements | None
    retailers: list[str] | None

    class Config:
        orm_mode = True
