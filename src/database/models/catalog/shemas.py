"""Product catalog validation schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field


class GroupBase(BaseModel):
    """GroupBase validation schema."""

    name: str = Field(max_length=100)


class Group(GroupBase):
    """Group validation schema."""

    id: int = Field(gt=0)
    content: list[Product]


class ProductBase(BaseModel):
    """ProductBase validation schema."""

    name: str = Field(max_length=150)
    group_id: int = Field(gt=0)


class Product(BaseModel):
    """Product validation schema."""

    id: int = Field(gt=0)
    parent: Group
    links: list[str]
