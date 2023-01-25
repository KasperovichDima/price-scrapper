"""Parser catalog validation schemas.
TODO: Add more validation data."""
from project_typing import ElType

from pydantic import BaseModel


class CategoryFactoryIn(BaseModel):
    el_type: ElType


class SubCategoryFactoryIn(CategoryFactoryIn):
    category_name: str


class GroupFactoryIn(SubCategoryFactoryIn):
    subcategory_name: str | None


class ProductFactoryIn(GroupFactoryIn):
    group_name: str
    url: str
