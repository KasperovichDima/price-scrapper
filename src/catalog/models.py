"""Product catalog models."""
from database import Base

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Element(Base):
    """Base class for all classes of product catalog."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)


class Group(Element):
    """Product group class."""

    __tablename__ = 'group'

    name = Column(String(100), index=True)
    content = relationship('Product', back_populates='parent')


class Product(Element):
    """Product class."""

    __tablename__ = "product"

    name = Column(String(150), index=True)
    group_id = Column(Integer, ForeignKey('group.id'))

    parent = relationship('Group', back_populates='content')
    pages = relationship('WebPage', back_populates='product')
