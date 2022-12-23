"""Core custom datatypes."""
from collections import namedtuple
from typing import Generator, NamedTuple

from catalog.models import BaseCatalogElement
from catalog.models import Folder

from retailer.models import Retailer


class RequestObjects(NamedTuple):
    """Objects to be added to request."""

    folders: list[BaseCatalogElement]
    products: list[BaseCatalogElement]
    retailers: list[Retailer]


ObjectParents = namedtuple('FolderParents', 'grand_parent_name parent_name')

BaseFactoryReturnType = Generator[BaseCatalogElement, None, None]
FolderReturnType = Generator[Folder, None, None]
