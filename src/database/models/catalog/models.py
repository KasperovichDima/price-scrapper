"""Product catalog models."""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ...config import Base


class Group(Base):
    """Product group class."""

    __tablename__ = 'group'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    content = relationship('Product', back_populates='parent')


class Product(Base):
    """Product class."""

    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), index=True)
    group_id = Column(Integer, ForeignKey('group.id'))

    parent = relationship('Group', back_populates='content')
    pages = relationship('WebPage', back_populates='product')
