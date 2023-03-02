"""Tavria parser typing."""
from collections import deque
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Protocol, Type

import aiohttp

from catalog.models import BaseCatalogElement

from project_typing import PriceRecord


Path = tuple[str, str | None, str | None]

NameRetailPromo = tuple[str, Decimal, Decimal | None]


# class Retailer_P(Protocol):
#     """Retailer model protocol. Provides variables: home_url, id."""

#     id: int
#     home_url: str


class ResultHandler_P(Protocol):
    # TODO: DO we need it?

    def __init__(self, parent_path: Path) -> None: ...

    def add_record(self, record: NameRetailPromo) -> None: ...

    async def update(self) -> None: ...


class FactoryResults_P(Protocol):
    """
    Represents Price factory work results with methods:
    1. 'add_record' method to add new factory record.
    2. 'get_price_records' to return result records.
    """

    retailer_id: int
    parent_path: Path
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
    """ProductFactory collects product names and prices from specified page
    and pages's paginated content. Then send them to product box, where they
    will be processed and saved. Provides next method:
    1. 'run' method to start factory. aio_session needed."""

    _main_url: str

    def __init__(self, url: str) -> None: ...

    async def run(self, aio_session: aiohttp.ClientSession) -> None:
        """Run factory to add it results to box."""


class FactoryCreator_P(Protocol):
    """Use group tags from target page to create product factories."""

    def create(self) -> deque[Factory_P]:
        """Creates and returns new factories."""


class Catalog_P(Protocol):
    """Implementation of product catalog tree. Main functions are:
        1. update - synchronize catalog structure in database with web page.
        2. get_id_by_path - will return you id of folder, specified by path."""

    async def update(self) -> None:
        """Get actual data from the page
        and update in_db catalog structure."""

    def get_id_by_path(self, path: Path) -> int:
        """Get id of folder with specified path."""


@dataclass(repr=False, eq=False, kw_only=True, frozen=True, slots=True)
class ToSwitchStatus:
    """Contains information about objects, whose
    'deprecated' status needs to be changed.
    NOTE: All objects must have same class."""

    cls_: Type[BaseCatalogElement]
    ids_to_depr: Iterable[int]
    ids_to_undepr: Iterable[int]
