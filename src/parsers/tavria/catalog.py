from typing import Iterable, Protocol

from catalog.models import BaseCatalogElement


class Catalog_P(Protocol):

    def __init__(self, elements: Iterable[BaseCatalogElement]) -> None:
        pass

    def check_element


class Catalog:

    def __init__(self, elements: Iterable[BaseCatalogElement]) -> None:
        pass

