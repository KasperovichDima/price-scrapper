"""Core validation schamas."""
from __future__ import annotations

from project_typing import cat_elements

from pydantic import BaseModel


class RequestDataScheme(BaseModel):
    """RequestData  validation scheme."""

    el_names: cat_elements | None
    shop_names: list[str] | None

    class Config:
        orm_mode = True
