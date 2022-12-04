"""Product catalog models and get model function."""
from typing import Type

from database.config import Base

import interfaces as i

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from .exceptions import wrong_model_exception


class Element(Base, i.IElement):  # type: ignore
    """Base class for all classes of product catalog."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)  # type: ignore

    def __repr__(self) -> str:
        return self.name


class Subgroup(Element):
    """Product group class."""

    __tablename__ = 'subgroup'

    name = Column(String(100), index=True)
    content = relationship('Product', back_populates='parent')  # type: ignore


class Product(Element, i.IProduct):
    """Product class."""

    __tablename__ = "product"

    name = Column(String(150), index=True)
    subgroup_id = Column(Integer, ForeignKey('subgroup.id'))

    prime_cost = Column(Numeric(scale=2))

    parent: Element = relationship('Subgroup', back_populates='content')  # type: ignore  # noqa: E501


def get_model(name: str) -> Type[Element]:
    """Get catalog element class by class name."""
    try:
        return eval(name)
    except NameError:
        raise wrong_model_exception
