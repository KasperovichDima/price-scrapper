"""Product catalog models and get model function."""
import interfaces as i

from models import BaseWithRepr

from project_typing import CatType

from sqlalchemy import Column, Enum, ForeignKey, Integer, Numeric, String


# class CatalogBase(Base, i.IElement):  # type: ignore
#     """Base class for all classes of product catalog."""

#     __abstract__ = True

#     id = Column(Integer, primary_key=True, index=True)  # type: ignore

#     def __repr__(self) -> str:
#         return self.name

#     def __eq__(self, __o: object) -> bool:
#         return self.id == __o.id


class Folder(BaseWithRepr, i.IFolder):
    """Product folder class."""

    __tablename__ = 'folder'

    name = Column(String(100), index=True, nullable=False)
    parent_id = Column(Integer, index=True)
    type = Column(Enum(CatType), nullable=False)


class Product(BaseWithRepr, i.IProduct):
    """Product class."""

    __tablename__ = "product"

    name = Column(String(150), index=True, nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey('folder.id'), nullable=False)
    prime_cost = Column(Numeric(scale=2))

    type = CatType.PRODUCT
