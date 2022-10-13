"""
SQLAlchemy models.
get_cat_model_by_name function - returns catalog models class by specified name.
get_inline_model_by_name function - return inline model class of element.
TODO:
cascade delete
many to many or one to many
add nullable=False
"""
from __future__ import annotations
from typing import Dict, Iterable, Optional, Type

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic.dataclasses import dataclass

import project_typing  as pt
from db_config import Base
import interfaces as i


class CatalogElement(i.ICatalogElement, Base):
    """Represents any item of product catalog."""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)

    content_class: Optional[str]
    content: Iterable[CatalogElement]

    def get_products(self) -> Iterable[i.ICatalogElement]:
        """
        Get inline elements of current element.
        TODO: Optimization needed.
        """
        products = []
        for _ in self.content:
            products.extend(_.get_products())
        return products

    def __repr__(self) -> str:
        return self.name


class Product(CatalogElement):
    """Product class."""
    __tablename__ = "products"

    name = Column(String(150), index=True)
    subgroup_id = Column(Integer, ForeignKey('subgroups.id'))
    content_class = None

    parent = relationship('SubGroup', back_populates='content')
    links = relationship('SubgroupURL', back_populates='product')

    def get_products(self) -> Iterable[CatalogElement]:
        """Product instance just return itself."""
        return self


class SubGroup(CatalogElement):
    """Product subgroup class."""
    __tablename__ = "subgroups"

    group_id = Column(Integer, ForeignKey('groups.id'))
    content_class = pt.ElNames.PRODUCT.value

    parent = relationship('Group', back_populates='content')
    content = relationship('Product', back_populates='parent')

    def get_products(self) -> Iterable[CatalogElement]:
        return self.content


class Group(CatalogElement):
    """Product group class."""
    __tablename__ = "groups"

    subgcategory_id = Column(Integer, ForeignKey('subcategories.id'))
    content_class = pt.ElNames.SUBGROUP.value

    parent = relationship('SubCategory', back_populates='content')
    content = relationship('SubGroup', back_populates='parent')


class SubCategory(CatalogElement):
    """Product subcategory class."""
    __tablename__ = "subcategories"

    category_id = Column(Integer, ForeignKey('categories.id'))
    content_class = pt.ElNames.GROUP.value

    parent = relationship('Category', back_populates='content')
    content = relationship('Group', back_populates='parent')


class Category(CatalogElement):
    """Product category class."""
    __tablename__ = "categories"
    content_class = pt.ElNames.SUBCATEGORY.value

    content = relationship('SubCategory', back_populates='parent')


class Shop(i.IShop, Base):
    """Internet shop class."""
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    home_url = Column(String(100))


class User(i.IUser, Base):
    """User class."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(20), index=True)
    last_name = Column(String(40), index=True)
    email = Column(String(100), index=True)
    is_active = Column(Boolean, default=False)
    type = Column(Enum(pt.UserType), default=pt.UserType.USER)

    def __repr__(self) -> str:
        return f'{self.first_name} {self.last_name}'


class Report(i.IReport, Base):
    """Report class. Contain all report data. Has a link to it's content."""
    __tablename__ = 'reports'

    def __init__(self, name: str, note: str, user_id: int) -> None:
        self.name = name
        self.note = note
        self.user_id = user_id

    id = Column(Integer, primary_key=True, index=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String(100), index=True)
    note = Column(String(250))
    user_id = Column(Integer, ForeignKey('users.id'))

    content = relationship('ReportLine', back_populates='report')

@dataclass(repr=False, eq=False, )
class ReportLine(i.IReportString, Base):
    """Every instance represents one report line."""
    __tablename__ = 'report_lines'

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(ForeignKey('reports.id'))
    product_id = Column(ForeignKey('products.id'))
    shop_id = Column(ForeignKey('shops.id'))
    retail_price = Column(Float)
    promo_price = Column(Float)

    report = relationship('Report', back_populates='content')
    product = relationship('Product')
    shop = relationship('Shop')


class SubgroupURL(Base):
    """Subgroups url class."""
    __tablename__ = 'subgrp_urls'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(ForeignKey('products.id'))
    shop_id = Column(ForeignKey('shops.id'))
    url_id = Column(ForeignKey('urls.id'))

    product = relationship('Product', back_populates='links')
    shop = relationship('Shop')
    url = relationship('URL')


class URL(Base):
    """URL adresses."""
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True, index=True)
    subgrp_url = Column(String(250))

    def __repr__(self) -> str:
        return self.subgrp_url


__CATALOG_MODELS: Dict[str, Type[CatalogElement]] = {
    pt.ElNames.CATEGORY.value: Category,
    pt.ElNames.SUBCATEGORY.value: SubCategory,
    pt.ElNames.GROUP.value: Group,
    pt.ElNames.SUBGROUP.value: SubGroup,
    pt.ElNames.PRODUCT.value: Product
}


def get_model_by_name(name: pt.ElNames) -> Type[CatalogElement]:
    """Get model of catalog by specified name."""
    return __CATALOG_MODELS[name.value]
