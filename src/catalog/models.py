"""Product catalog models and get model function."""
from base_models import BaseWithRepr

from project_typing import ElType

from sqlalchemy import Boolean, Column, Enum, ForeignKey
from sqlalchemy import Integer, Numeric, String


class BaseCatalogElement(BaseWithRepr):

    __abstract__ = True

    name: Column
    parent_id: Column
    el_type: Column
    deprecated = Column(Boolean, default=False)

    def __hash__(self) -> int:
        return hash((self.name, self.parent_id))


class Folder(BaseCatalogElement):
    """Product folder class."""

    __tablename__ = 'folder'

    name = Column(String(100), index=True, nullable=False)
    parent_id = Column(Integer, index=True)
    el_type = Column(Enum(ElType), nullable=False)


class Product(BaseCatalogElement):
    """Product class."""

    __tablename__ = "product"

    # site_id = Column(Integer, index=True, nullable=False, unique=True)
    name = Column(String(150), index=True, nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey('folder.id', ondelete='CASCADE'),
                       nullable=False)
    prime_cost = Column(Numeric(scale=2))

    el_type = ElType.PRODUCT  # type: ignore
