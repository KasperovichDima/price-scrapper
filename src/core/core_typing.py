"""Core custom datatypes."""
from typing import NamedTuple

from catalog.models import BaseCatalogElement

from retailer.models import Retailer


class RequestObjects(NamedTuple):
    """Objects to be added to request."""

    folders: list[BaseCatalogElement]
    products: list[BaseCatalogElement]
    retailers: list[Retailer]
