"""Core custom datatypes."""
from collections import namedtuple
from typing import Generator, NamedTuple

from catalog.models import BaseCatalogElement

from retailer.models import Retailer


class RequestObjects(NamedTuple):
    """Objects to be added to request."""

    folders: list[BaseCatalogElement]
    products: list[BaseCatalogElement]
    retailers: list[Retailer]


ObjectParents = namedtuple('ObjectParents', 'grand_parent_name parent_name')

BaseFactoryReturnType = Generator[BaseCatalogElement, None, None]
