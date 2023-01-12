"""Product catalog models and get model function."""
from base_models import BaseWithRepr

from project_typing import ElType

from sqlalchemy import Column, Enum, ForeignKey, Integer, Numeric, String


class BaseCatalogElement(BaseWithRepr):

    __abstract__ = True

    name: Column(String)
    parent_id: Column(Integer)
    el_type: Column(Enum(ElType))

    def __hash__(self) -> int:
        return hash((self.name, self.parent_id, self.el_type))


class Folder(BaseCatalogElement):
    """Product folder class."""

    __tablename__ = 'folder'

    name = Column(String(100), index=True, nullable=False)
    parent_id = Column(Integer, index=True)
    el_type = Column(Enum(ElType), nullable=False)


class Product(BaseCatalogElement):
    """Product class."""

    __tablename__ = "product"

    name = Column(String(150), index=True, nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey('folder.id', ondelete='CASCADE'),
                       nullable=False)
    prime_cost = Column(Numeric(scale=2))

    el_type = ElType.PRODUCT  # type: ignore
