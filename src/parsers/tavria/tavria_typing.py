"""Tavria parser typing."""
from collections import deque
from typing import Generator, NamedTuple, Protocol

import aiohttp

from catalog.models import BaseCatalogElement


class ObjectParents(NamedTuple):
    # FIXME: Duplicating with parents
    gp_name: str | None = None
    p_name: str | None = None

    def __bool__(self) -> bool:
        return any((self.gp_name, self.p_name))


BaseFactoryReturnType = Generator[BaseCatalogElement, None, None]

Parents = tuple[str, str | None, str]

NameRetailPromo = tuple[str, float, float | None]


class Factory_P(Protocol):
    """Factory protocol."""

    _main_url: str

    def __init__(self, url: str, retailer_id: int) -> None:
        ...

    async def run(self, aio_session: aiohttp.ClientSession) -> None:
        """Run factory to add it results to box."""


class FactoryCreator_P(Protocol):
    """FactoryCreator protocol."""

    def create(self) -> deque[Factory_P]:
        """Create new factories. Retailer must be specified."""


class Catalog_P(Protocol):
    """Catalog updater protocol."""

    async def update(self) -> None:
        """Get actual data from the page
        and update in db catalog structure.""" 
