"""Catalog utils."""
from project_typing import ElType

from .models import Folder, Product


def get_catalog_class(type_: ElType) -> type[Product] | type[Folder]:
    """Get catalog class by ElType."""
    """TODO: Check if we need it!"""
    return Product if type_ is ElType.PRODUCT else Folder
