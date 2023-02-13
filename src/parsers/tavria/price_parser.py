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

from core.models import PriceLine

import crud

from parsers import exceptions as e

from project_typing import PriceRecord

from retailer.models import Retailer
from retailer.retailer_typing import RetailerName

from sqlalchemy.orm import Session

from . import constants as c
from . import utils as u
from .tavria_typing import NameRetailPromo, Parents
from .tavria_typing import Catalog_P
from .tavria_typing import FactoryCreator_P
from .tavria_typing import Factory_P


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
        self._parents_to_id = await u.get_groups_parent_to_id(db_session)
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


box = Box()


class PriceFactory:

    """Factory collects price records from page and pages's
    paginated content and transfer them to the box."""

    _product_tags: ResultSet[Tag]
    _results: FactoryResults

    __PARSER_ERROR_MSG = """
    Something went wrong while parsing {}...
    """

    def __init__(self, url: str, retailer_id: int) -> None:
        self._main_url = self._url = url
        self._results = FactoryResults(
            retailer_id=retailer_id,
        )

    async def run(self, aio_session: aiohttp.ClientSession) -> None:
        """Run factory to add it results to box."""

        self._aio_session = aio_session
        try:
            await self._get_page_tags()
        except e.UnexpectedParserError:
            return
        self._collect_prices()
        self._results.parents = self.parents
        await self._get_paginated_content()
        await box.add(self._results)

    async def _get_page_tags(self) -> None:
        await self._get_product_area()
        self._get_product_tags()

    async def _get_product_area(self) -> None:
        self._product_area = bs(await self._get_page_html(), 'lxml')\
            .find('div', {'class': "catalog-products"})

    async def _get_page_html(self) -> str | None:
        async with self._aio_session.get(self._url) as rsp:
            if rsp.status != 200:
                #  TODO: add log and email developer here
                raise e.UnexpectedParserError(
                    self.__PARSER_ERROR_MSG.format(self._url)
                )
            return await rsp.text()

    def _get_product_tags(self) -> None:
        self._product_tags = self._product_area\
            .find_all('div', {'class': "products__item"})

    @property
    def parents(self) -> Parents:
        first_tag = self._product_tags[0]
        c_name = first_tag.get('data-item_category3')
        s_name = first_tag.get('data-item_category2')
        return (
            c_name if c_name else s_name,
            s_name if c_name else None,
            first_tag.get('data-item_category')
        )

    def _collect_prices(self) -> None:
        for tag in self._product_tags:
            self._results.add_record(
                (tag.get('data-name'),
                 float(tag.get('data-price')),
                 self._get_promo_price(tag))
            )

    @staticmethod
    def _get_promo_price(tag: Tag) -> float | None:  # type: ignore
        if promo := tag.find('span', {'class': 'price__discount'}):
            return float(promo.text.strip().removesuffix(' ₴'))

    @property
    def _page_is_paginated(self) -> bool:
        return bool(self._paginator_size)

    @cached_property
    def _paginator_size(self) -> int:  # type: ignore
        for tag in self._paginator[::-1]:
            if tag.attrs.get('aria-label') == 'Next':
                return int(tag.get('href').split('=')[-1])
        return 0

    @property
    def _paginator(self) -> ResultSet[Tag]:
        return self._product_area.find(
            'div', {'class': 'catalog__pagination'}
        ).find_all('a')

    async def _get_paginated_content(self):
        if not self._page_is_paginated:
            return
        tasks = (self._page_task(url) for url in self._paginated_urls)
        await asyncio.gather(*tasks)

    async def _page_task(self, url: str) -> None:
        """TODO: Try to remove it."""
        self._url = url
        try:
            await self._get_page_tags()
        except e.UnexpectedParserError:
            return
        self._collect_prices()

    @property
    def _paginated_urls(self) -> Generator[str, None, None]:
        return (f'{self._url}?page={_}'
                for _ in range(2, self._paginator_size + 1))

    def __repr__(self) -> str:
        return self._url

    def __hash__(self) -> int:
        return hash(self._main_url)

    def __eq__(self, __o: object) -> bool:
        return self._main_url == __o._main_url  # type: ignore


class FactoryCreator:
    """
    Makes request to source url.
    Parses tags, extracts data.
    Prapares data for objects creation.
    """
    _factories: deque[Factory_P] = deque()

    def __init__(self, retailer: Retailer, factory_cls: type[Factory_P]) -> None:
        self.retailer = retailer
        self._factory_cls = factory_cls

    def create(self) -> deque[Factory_P]:
        for tag in u.get_group_tags(self.retailer.home_url):  # type: ignore
            if url := u.get_url(tag):
                factory = self._factory_cls(url, self.retailer.id)  # type: ignore
                self._factories.append(factory)

        self._remove_discount_page()
        return self._factories

    def _remove_discount_page(self) -> None:
        """FIXME: Duplicating in utils."""
        if 'discount' in str(self._factories[0]):
            self._factories.popleft()


class PriceParser:

    """Parser for collecting prices from specified retailer's web page."""

    _factories: deque[Factory_P]

    def __init__(self, catalog: Catalog_P,
                 f_creator: FactoryCreator_P) -> None:
        self._catalog = catalog
        self._f_creator = f_creator

    async def update_catalog(self) -> None:
        await self._catalog.update()
        del self._catalog

    async def update_products(self) -> None:

        await self._get_factories()
        while self._factories:
            self._get_next_batch()
            async with u.aiohttp_session_maker() as aio_session:
                tasks = (self._single_factory_task(factory, aio_session)
                         for factory in self._factory_batch)
                await self._complete_tasks(tasks)

    async def _get_factories(self) -> None:
        self._factories = self._f_creator.create()
        del self._f_creator

    def _get_next_batch(self) -> None:
        self._factory_batch = {self._factories.pop()
                               for _ in range(self._batch_size)}

    @property
    def _batch_size(self) -> int:
        return c.TAVRIA_FACTORIES_PER_SESSION\
            if c.TAVRIA_FACTORIES_PER_SESSION\
            <= len(self._factories)\
            else len(self._factories)

    async def _single_factory_task(self, factory: Factory_P,
                                   aio_session) -> None:
        print(f'{factory} in progress...')
        await factory.run(aio_session)
        self._factory_batch.remove(factory)

    async def _complete_tasks(self, tasks) -> None:
        try:
            await asyncio.gather(*tasks)
            u.tasks_are_finished()
        except asyncio.exceptions.TimeoutError:
            if self._factory_batch:
                self._factories.extend(self._factory_batch)
