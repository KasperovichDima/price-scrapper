"""
Product catalog models and get model function.
TODO: Remove ElType. Just Folder and Product.
      If Folder has no parents - it is Category.
      If Folder has parent and childs - it is subcategory.
      If Folder has no childrens - it is a grouop.
"""
from base_models import BaseWithRepr

from sqlalchemy import Boolean, Column, ForeignKey
from sqlalchemy import Integer, Numeric, String


class BaseCatalogElement(BaseWithRepr):

    __abstract__ = True

    name: Column[String]
    parent_id: Column[Integer]
    el_type: Column
    deprecated = Column(Boolean, default=False)

    def __hash__(self) -> int:
        return hash((self.name, self.parent_id))


class Folder(BaseCatalogElement):
    """Product folder class."""
    #  TODO: ondelete='CASCADE'?
    __tablename__ = 'folder'

    name = Column(String(100), index=True, nullable=False)
    parent_id = Column(Integer, index=True)


class Product(BaseCatalogElement):
    """
    Product class.
    NOTE: unique in product name was removed after finding duplicate
    names on site. But on my opinion this option is required.
    """

    __tablename__ = "product"

    name = Column(String(150), index=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('folder.id', ondelete='CASCADE'),
                       nullable=False)
    prime_cost = Column(Numeric(scale=2))
