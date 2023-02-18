"""Tavria parser typing."""
from collections import deque
from decimal import Decimal
from typing import Iterator, Protocol

import aiohttp

from project_typing import PriceRecord


Path = tuple[str, str | None, str | None]

NameRetailPromo = tuple[str, Decimal, Decimal | None]


class Retailer_P(Protocol):
    """Retailer model protocol. Provides variables: home_url, id."""

    id: int
    home_url: str


class FactoryResults_P(Protocol):
    """FactoryResults protocol. Provides signatures for:
    1. 'add_record' method to add new factory record.
    2. 'get_price_records' to return result records.

    Also supports variables: retailer_id, parents, records.
    """

    retailer_id: int
    parents: Path | None = None
    records: deque[NameRetailPromo]

    def add_record(self, record: NameRetailPromo) -> None:
        """Add new record form factory of type NameRetailPromo."""

    def get_price_lines(self, prod_name_to_id_table: dict[str, int]
                        ) -> set[PriceRecord]:
        """
        Returns tuples:
        (product_id, retailer_id, retail_price, promo_price)
        """


class Factory_P(Protocol):
    """Factory protocol. Provides signatures for:
    1. 'run' method to start factory.
    2. '__init__' method for initialization."""

    _main_url: str

    def __init__(self, url: str, retailer_id: int) -> None:
        ...

    async def run(self, aio_session: aiohttp.ClientSession) -> None:
        """Run factory to add it results to box."""


class FactoryCreator_P(Protocol):
    """FactoryCreator protocol. Provides signature for create method."""

    def create(self) -> deque[Factory_P]:
        """Creates and returns new factories."""


class Catalog_P(Protocol):
    """Catalog updater protocol. Provides signature for update method."""

    async def update(self) -> None:
        """Get actual data from the page
        and update in db catalog structure."""
