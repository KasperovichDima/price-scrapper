"""Product catalog models and get model function."""
from typing import Iterable, Type

from database.config import Base

import interfaces as i

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .exceptions import wrong_model_exception


class Element(Base, i.IElement):
    """Base class for all classes of product catalog."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)


class Group(Element):
    """Product group class."""

    __tablename__ = 'group'

    name = Column(String(100), index=True)
    content = relationship('Product', back_populates='parent')


class Product(Element, i.IProduct):
    """Product class."""

    __tablename__ = "product"

    name = Column(String(150), index=True)
    group_id = Column(Integer, ForeignKey('group.id'))

    parent = relationship('Group', back_populates='content')
    pages = relationship('WebPage', back_populates='product')

    @property
    def content(self) -> Iterable[i.IElement]:
        """Content of current catalog instance."""

        return (self,)
    
    def __repr__(self) -> str:
        return self.name


def get_model(name: str) -> Type[Element]:
    """Get catalog element class by class name."""
    try:
        return eval(name)
    except NameError:
        raise wrong_model_exception
