"""Product catalog validation schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field


class GroupBase(BaseModel):
    """GroupBase validation schema."""

    name: str = Field(max_length=100)


class GroupScheme(GroupBase):
    """Group validation schema."""

    id: int = Field(gt=0)
    content: list[ProductScheme]


class ProductBase(BaseModel):
    """ProductBase validation schema."""

    name: str = Field(max_length=150)
    group_id: int = Field(gt=0)


class ProductScheme(BaseModel):
    """Product validation schema."""

    id: int = Field(gt=0)
    parent: GroupScheme
    links: list[str]


class ElementScheme(BaseModel):
    """Validation scheme for content of catalog element."""

    id: int
    name: str

    class Config:
        orm_mode = True


class GetElementScheme(BaseModel):
    """GetElement validation scheme to be used in get_content function."""

    model: str | None = None
    content: list[ElementScheme] | None = None
