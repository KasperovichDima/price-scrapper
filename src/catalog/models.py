"""Product catalog models and get model function."""
import interfaces as i

from models import BaseWithRepr

from project_typing import ElType

from sqlalchemy import Column, Enum, ForeignKey, Integer, Numeric, String


class Folder(BaseWithRepr, i.ICatalogElement):
    """Product folder class."""

    __tablename__ = 'folder'

    name = Column(String(100), index=True, nullable=False)
    parent_id = Column(Integer, index=True)
    type = Column(Enum(ElType), nullable=False)


class Product(BaseWithRepr, i.ICatalogElement):
    """Product class."""

    __tablename__ = "product"

    name = Column(String(150), index=True, nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey('folder.id'), nullable=False)
    prime_cost = Column(Numeric(scale=2))

    type = ElType.PRODUCT
