"""
Tavria price parser.
TODO: Merge with other.
"""
from __future__ import annotations

import asyncio
from collections import deque
from functools import cached_property
from typing import Generator, Iterable

import aiohttp

from bs4 import BeautifulSoup as bs
from bs4 import ResultSet, Tag

from catalog.models import Product
from catalog.utils import get_class_by_type

from core.models import PriceLine

import crud

from parsers import exceptions as e

from project_typing import ElType, PriceRecord

from retailer.models import Retailer
from retailer.retailer_typing import RetailerName

from sqlalchemy.orm import Session

from . import constants as c
from . import utils as u
from .tavria_typing import NameRetailPromo, Parents
from .tavria_typing import FactoryCreator_P, Factory_P


class FactoryResults:
    """Represents Price factory work
    results with get_records method."""

    __slots__ = ('retailer_id', 'parents', 'records')

    def __init__(self, retailer_id: int) -> None:
        self.retailer_id = retailer_id
        self.parents: Parents | None = None
        self.records: deque[NameRetailPromo] = deque()

    def add_record(self, record: NameRetailPromo) -> None:
        self.records.append(record)

    def get_price_records(self, prod_name_to_id_table: dict[str, int]
                          ) -> zip[PriceRecord]:
        """
        Returns tuples:
        (product_id, retailer_id, retail_price, promo_price)
        """

        return zip(
            (prod_name_to_id_table[rec[0]] for rec in self.records),
            (self.retailer_id for _ in self.records),
            (rec[1] for rec in self.records),
            (rec[2] for rec in self.records),
            strict=True
        )


class Box:
    """
    1. Get in_base products
    2. Get result product's names
    3. Deprecate, undeprecate, create new

    4. Get in_base price lines
    5. Create inique lines
    """

    _group_products: list[Product]
    _db_session: Session
    _parents_to_id: dict[Parents, int]

    __NOT_INIT_MSG = """
    Box is not initialized. It seems, you 
    forgot to await 'initialize' method first.
    """

    __initialized = False

    async def initialize(self, db_session: Session) -> None:
        """Initialize box with db_session, which is required for
        it's work. Also parents_to_id table will be created."""
        self._db_session = db_session
        self._parents_to_id = await u.get_parent_id_table(db_session)
        self.__initialized = True

    async def add(self, factory_results: FactoryResults) -> None:
        """Add factory results to box. Data will be processed and saved."""
        if not self.__initialized:
            raise e.NotInitializedError(self.__NOT_INIT_MSG)

        self._factory_results = factory_results
        self._group_products = await crud.get_products(
            self._db_session, folder_ids=(self._folder_id,)
        )
        await self._refresh_products()
        await self._refresh_price_lines()

    @property
    def _folder_id(self) -> int:
        assert self._factory_results.parents
        return self._parents_to_id[self._factory_results.parents]

    async def _refresh_products(self) -> None:
        # FIXME: Long method.
        actual_prod_names = deprecated_prod_names = set()
        for product in self._group_products:
            if product.deprecated:
                deprecated_prod_names.add(product.name)
            else:
                actual_prod_names.add(product.name)

        new_names = {_[0] for _ in self._factory_results.records}
        to_create_names = new_names - deprecated_prod_names - actual_prod_names
        to_create_objects = (Product(name=_, parent_id=self._folder_id)
                             for _ in to_create_names)
        await crud.add_instances(to_create_objects, self._db_session)
        # TODO: Remove redundant sets
        to_deprecate = actual_prod_names - new_names
        to_undeprecate = deprecated_prod_names & new_names
        to_switch_depr_names = to_deprecate.union(to_undeprecate)
        to_switch_depr_objects = (_ for _ in self._group_products
                                   if _.name in to_switch_depr_names)
        await crud.switch_deprecated(to_switch_depr_objects, self._db_session)

    async def _refresh_price_lines(self) -> None:
        if new_records := await self._get_unique_records():
            await crud.add_instances(new_records, self._db_session)

    async def _get_unique_records(self) -> Iterable[PriceLine] | None:
        records = set(
            self._factory_results.get_price_records(self._prod_name_to_id)
        )
        records.difference_update(await self._last_price_lines)
        return (PriceLine.from_tuple(rec) for rec in records)\
            if records else None

    @property
    def _prod_name_to_id(self) -> dict[str, int]:
        return {_.name: _.id for _ in self._group_products}

    @property
    async def _last_price_lines(self) -> list[PriceLine]:
        prod_ids = (_.id for _ in self._group_products)
        return await crud.get_last_price_lines(
            prod_ids, self._factory_results.retailer_id, self._db_session
        )
