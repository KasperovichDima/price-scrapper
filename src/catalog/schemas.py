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
