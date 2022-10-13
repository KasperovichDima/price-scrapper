"""Models validation by Pydantic"""
from __future__ import annotations
from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr

from project_typing import ShopName
from project_typing import UserType


class CatalogElementBase(BaseModel):
    """CatalogElementBase validation."""
    name: str


class CatalogElementCreate(CatalogElementBase):
    """CatalogElementCreate validation."""


class CatalogElement(CatalogElementBase):
    """CatalogElement validation."""
    id: int


class CategoryBase(BaseModel):
    """CategoryBase validation."""
    name: str


class CategoryCreate(CategoryBase):
    """CategoryCreate validation."""


class Category(CategoryBase):
    """Category validation."""
    id: int
    subcategories: List[SubCategory] = []

    class Config:
        orm_mode = True


class SubCategoryBase(BaseModel):
    """SubCategoryBase validation."""
    name: str


class SubCategoryCreate(SubCategoryBase):
    """SubCategoryCreate validation."""


class SubCategory(SubCategoryBase):
    """SubCategory validation."""
    id: int
    category_id: int
    category: Category
    groups: List[Group] = []

    class Config:
        orm_mode = True


class GroupBase(BaseModel):
    """GroupBase validation."""
    name: str


class GroupCreate(GroupBase):
    """GroupCreate validation."""


class Group(GroupBase):
    """Group validation."""
    id: int
    subgcategory_id: int
    subgcategory: SubCategory
    subgroups: List[SubGroup] = []

    class Config:
        orm_mode = True


class SubGroupBase(BaseModel):
    """SubGroupBase validation."""
    name: str


class SubGroupCreate(SubGroupBase):
    """SubGroupCreate validation."""


class SubGroup(SubGroupBase):
    """SubGroup validation."""
    id: int
    group_id: int
    group: Group
    products: List[Product] = []

    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    """ProductBase validation."""
    name: str


class ProductCreate(ProductBase):
    """ProductCreate validation."""


class Product(ProductBase):
    """Product validation."""
    id: int
    subgroup_id: int

    class Config:
        orm_mode = True


class ShopBase(BaseModel):
    """ShopBase validation."""
    name: ShopName
    home_url: str


class ShopCreate(ShopBase):
    """ShopCreate validation."""


class Shop(ShopBase):
    """Shop validation."""
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    """UserBase validation."""
    first_name: str
    last_name: str
    email: EmailStr


class UserCreate(UserBase):
    """UserCreate validation."""


class User(UserBase):
    """User validation."""
    id: int
    is_active: bool
    type: UserType
    reports: List[ReportHeader] = []

    class Config:
        orm_mode = True


class ReportHeaderBase(BaseModel):
    """ReportHeaderBase validation."""
    name: str
    note: str


class ReportHeaderCreate(ReportHeaderBase):
    """ReportHeaderCreate validation."""
    user: User


class ReportHeader(ReportHeaderBase):
    """ReportHeader validation."""

    id: int
    user_id: int
    time_created: datetime

    class Config:
        orm_mode = True

# class ReportBase(BaseModel):
#     """ReportBase validation."""
#     name: str
#     note: str


# class ReportCreate(ReportBase):
#     """ReportCreate validation."""


# class Report(ReportBase):
#     """Report validation."""
#     id: int
#     user_id: int
#     user: User

#     class Config:
#         orm_mode = True


class SubgroupURLBase(BaseModel):
    """SubgroupURLBase validation."""
    subgrp_url: str


class SubgroupURLCreate(SubgroupURLBase):
    """SubgroupURLCreate validation."""


class SubgroupURL(SubgroupURLBase):
    """SubgroupURL validation."""
    id: int

    class Config:
        orm_mode = True
