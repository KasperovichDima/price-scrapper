"""
Tavria price parser.
TODO:
1. Classes refactoring [x]
2. naming refactoring [x]
3. flake 8
4. All TODOs
5. Add protocols
"""
from __future__ import annotations

import asyncio
from collections import deque
from functools import cached_property
from typing import Generator

import aiohttp

from bs4 import BeautifulSoup as bs
from bs4 import ResultSet, Tag

from catalog.models import Product

from core.models import PriceLine

import crud

from parsers.exceptions import UnexpectedParserError

from project_typing import PriceRecord, RetailerName

from retailer.models import Retailer

from sqlalchemy.orm import Session

from . import constants as c
from . import utils as u
from .tavria_typing import NameRetailPromo, Parents


class FactoryResults:
    """Represents Price factory work
    results with get_records method."""

    def __init__(self, retailer_id: int) -> None:
        self._retailer_id = retailer_id
        self._parents: Parents | None = None
        self._records: deque[NameRetailPromo] = deque()

    @property
    def retailer_id(self) -> int:
        return self._retailer_id

    def set_parents(self, parents: Parents) -> None:
        self._parents = parents

    def add_record(self, record: NameRetailPromo) -> None:
        self._records.append(record)

    def get_price_records(self, prod_name_to_id_table: dict[str, int]
                          ) -> zip[PriceRecord]:
        """
        Returns tuples:
        (product_id, retailer_id, retail_price, promo_price)
        """

        return zip(
            (prod_name_to_id_table[rec[0]] for rec in self._records),
            (self._retailer_id for _ in self._records),
            (rec[1] for rec in self._records),
            (rec[2] for rec in self._records),
            strict=True
        )


class Box:
    """TODO: Choose correct name. What if we will get new product name here?"""

    _group_products: list[Product]

    def __init__(self, db_session: Session,
                 parents_to_id: dict[Parents, int]) -> None:
        self._db_session = db_session
        self._parents_to_id = parents_to_id

    async def add(self, factory_results: FactoryResults) -> None:
        """Add factory results to box. Data will be processed and saved."""
        self._factory_results = factory_results
        await self._get_group_products()
        await self._save_new_records()

    async def _get_group_products(self) -> None:
        self._group_products = await crud.get_products(
            self._db_session, folder_ids=(self._folder_id,)
        )

    @property
    def _folder_id(self) -> int:
        return self._parents_to_id[self._factory_results._parents]

    async def _save_new_records(self) -> None:
        if new_records := await self._get_unique_records():
            await crud.add_instances(new_records, self._db_session)

    async def _get_unique_records(self) -> Generator[PriceLine] | None:
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


class PriceFactory:

    """Factory collects price records from page and pages's
    paginated content and transfer them to the box."""

    _product_tags: ResultSet[Tag]
    _paginator: ResultSet[Tag]
    _box: Box
    _results: FactoryResults

    def __init__(self, url: str, retailer_id: int) -> None:
        self._main_url = self._url = url
        self._results = FactoryResults(
            retailer_id=retailer_id,
        )

    async def __call__(self, aio_session: aiohttp.ClientSession) -> None:
        """Run factory to add it results to box."""

        self._aio_session = aio_session
        try:
            await self._get_page_tags()
        except UnexpectedParserError:
            return
        self._collect_prices()
        self._results.set_parents(self.parents)
        await self._get_paginated_content()
        await self._box.add(self._results)

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
                raise UnexpectedParserError(
                    f'something went wrong while parsing {self._url}...'
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
        except UnexpectedParserError:
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
        return self._main_url == __o._main_url


class FactoryCreator:
    """
    Makes request to source url.
    Parses tags, extracts data.
    Prapares data for objects creation.
    """
    _factories: deque[PriceFactory] = deque()
    retailer_id: int

    def __call__(self, home_url: str, retailer_id: int) -> deque[PriceFactory]:
        """
        TODO: Home url should be taken from retailer db object.
              Refactoring needed!
        """
        self.retailer_id = retailer_id  # FIXME
        for tag in u.get_group_tags(home_url):
            self.create_factory(tag)
        self.remove_discount_page()
        return self._factories

    def create_factory(self, tag) -> None:
        if url :=  u.get_url(tag):
            self._factories.append(PriceFactory(url, self.retailer_id))

    def remove_discount_page(self) -> None:
        if 'discount' in str(self._factories[0]):
            self._factories.popleft()


class PriceParser:

    """Parser for collecting prices from specified retailer's web page."""

    _factories: deque[PriceFactory]
    _retailer: Retailer

    async def refresh_prices(self, retailer_name: RetailerName,
                             db_session: Session) -> None:
        self._retailer = await crud.get_ratailer(retailer_name, db_session)
        PriceFactory._box = Box(db_session, await u.get_parent_id_table(db_session))
        self._get_factories()
        while self._factories:
            self._get_next_batch()
            async with u.aiohttp_session_maker() as aio_session:
                tasks = (self._single_factory_task(factory, aio_session)
                         for factory in self._factory_batch)
                await self._complete_tasks(tasks)

    def _get_factories(self) -> None:
        self._factories = FactoryCreator()(self._retailer.home_url,  # type: ignore
                                           self._retailer.id)  # type: ignore

    def _get_next_batch(self) -> None:
        self._factory_batch = {self._factories.pop()
                               for _ in range(self._batch_size)}

    @cached_property
    def _batch_size(self) -> int:
        return c.TAVRIA_FACTORIES_PER_SESSION\
            if c.TAVRIA_FACTORIES_PER_SESSION\
            <= len(self._factories)\
            else len(self._factories)

    async def _single_factory_task(self, factory: PriceFactory,
                                  aio_session) -> None:
        print(f'{factory} in progress...')
        await factory(aio_session)
        self._factory_batch.remove(factory)

    async def _complete_tasks(self, tasks) -> None:
        try:
            await asyncio.gather(*tasks)
            u.tasks_are_finished()
        except asyncio.exceptions.TimeoutError:
            if self._factory_batch:
                self._factories.extend(self._factory_batch)
