"""Product catalog validation schemas."""
from decimal import Decimal

from project_typing import CatType

from pydantic import BaseModel


class BaseCatScheme(BaseModel):
    """Base catalog instance scheme."""

    id: int
    name: str
    parent_id: int | None
    type: CatType

    class Config:
        orm_mode = True


class FolderScheme(BaseCatScheme):
    """Folder validation scheme."""


class ProductScheme(BaseCatScheme):
    """Product validation scheme."""

    prime_cost: Decimal


class FolderContent(BaseModel):
    """Model and validation scheme for content of specified folder."""

    folders: list[FolderScheme]
    products: list[ProductScheme]
