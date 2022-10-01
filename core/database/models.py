"""
SQLAlchemy models.

TODO:
cascade delete
many to many or one to many
add nullable=False
"""
from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base
from .db_typing import UserType


class Category(Base):
    """Product category class."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)

    subcategories = relationship('SubCategory', back_populates='category')


class SubCategory(Base):
    """Product subcategory class."""
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    category_id = Column(Integer, ForeignKey('categories.id'))

    category = relationship('Category', back_populates='category')
    groups = relationship('Group', back_populates='subcategory')


class Group(Base):
    """Product group class."""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    subgcategory_id = Column(Integer, ForeignKey('subcategories.id'))

    subgcategory = relationship('SubCategory', back_populates='groups')
    subgroups = relationship('SubGroup', back_populates='group')


class SubGroup(Base):
    """Product subgroup class."""
    __tablename__ = "subgroups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    group_id = Column(Integer, ForeignKey('groups.id'))

    group = relationship('Group', back_populates='subgcategory')
    products = relationship('Product', back_populates='subgroup')


class Product(Base):
    """Product class."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True)
    subgroup_id = Column(Integer, ForeignKey('subgroups.id'))

    subgroup = relationship('SubGroup', back_populates='products')


class Shop(Base):
    """Internet shop class."""
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    home_url = Column(String(100))


class User(Base):
    """User class."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(20), index=True)
    last_name = Column(String(40), index=True)
    email = Column(String(100), index=True)
    is_active = Column(Boolean, default=False)
    type = Column(Enum(UserType), default=UserType.USER)

    reports = relationship('Report', back_populates='user')


class Report(Base):
    """Monitoring report class."""
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    note = Column(String(250))
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='reports')


subgrp_url_by_shops = Table('subgrp_url_by_shops', Base.metadata,
    Column('subgrp_id', Integer, ForeignKey('subgroups.id')),
    Column('shop_id', Integer, ForeignKey('shops.id')),
)

report_data = Table('report_data', Base.metadata,
    Column('report_id', Integer, ForeignKey('reports.id')),
    Column('product_id', Integer, ForeignKey('products.id')),
    Column('shop_id', Integer, ForeignKey('shops.id')),
    Column('retail_price', Float)
)
