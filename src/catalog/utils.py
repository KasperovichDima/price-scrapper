"""Catalog utils."""
from project_typing import ElType

from . import models as m


def get_class_by_type(type_: ElType) -> type[m.BaseCatalogElement]:
    return m.Product if type_ is ElType.PRODUCT else m.Folder
