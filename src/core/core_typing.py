"""Core custom datatypes."""
from collections import namedtuple
from collections.abc import Mapping
from typing import Generator, NamedTuple, Protocol

from catalog.models import BaseCatalogElement
from catalog.models import Folder

from retailer.models import Retailer


class RequestObjects(NamedTuple):
    """Objects to be added to request."""

    folders: list[BaseCatalogElement]
    products: list[BaseCatalogElement]
    retailers: list[Retailer]


FolderData = namedtuple('FolderData', 'grand_parent_name parent_name')

BaseFactoryReturnType = Generator[BaseCatalogElement, None, None]
FolderReturnType = Generator[Folder, None, None]


class Factory(Protocol):
    def add_name(self, name: str) -> None: ...

    def get_objects(self,
                    folders: Mapping[FolderData, int]
                    ) -> BaseFactoryReturnType: ...
