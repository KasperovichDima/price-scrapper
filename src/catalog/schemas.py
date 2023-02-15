"""Product catalog validation schemas."""
from decimal import Decimal

from pydantic import BaseModel

from . import extra_schemas as es


class BaseCatScheme(BaseModel):
    """Base catalog instance scheme."""

    id: int
    name: str
    parent_id: int | None

    class Config:
        orm_mode = True


class FolderScheme(BaseCatScheme):
    """Folder validation scheme."""


class ProductScheme(BaseCatScheme):
    """Product validation scheme."""

    prime_cost: Decimal | None


class FolderContent(BaseModel):
    """Model and validation scheme for content of specified folder."""

    folders: list[FolderScheme] | None
    products: list[ProductScheme] | None

    class Config:
        schema_extra = es.folder_content
