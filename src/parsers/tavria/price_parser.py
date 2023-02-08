"""
Tavria price parser.
TODO:
1. Classes refactoring
2. naming refactoring
3. flake 8
4. All TODOs
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

from project_typing import ElType, RetailerName
from project_typing import PriceRecord

from pydantic import BaseModel

from sqlalchemy.orm import Session

from . import constants as c
from . import utils as u
from .tavria_typing import Parents


async def get_parent_id_table(db_session: Session) -> dict[Parents, int]:
    folders = await crud.get_folders(db_session)
    id_to_folder = {_.id: _ for _ in folders}
    parents_to_id: dict[Parents, int] = {}
    for group in (_ for _ in folders if _.el_type is ElType.GROUP):
        p_folder = id_to_folder[group.parent_id]
        gp_folder = id_to_folder.get(p_folder.parent_id)
        c_name = gp_folder.name if gp_folder else p_folder.name
        s_name = p_folder.name if gp_folder else None
        g_name = group.name
        parents = (c_name, s_name, g_name)
        parents_to_id[parents] = group.id
    return parents_to_id


NameRetailPromo = tuple[str, float, float | None]


class FactoryResults(BaseModel):
    """Represents Price factory work
    results with get_records method."""

    retailer_id: int
    parents: Parents
    records: deque[NameRetailPromo] = deque()

    def add_record(self, record: NameRetailPromo) -> None:
        self.records.append(record)

    def get_records(self, prod_name_to_id_table: dict[str, int]
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
        return self._parents_to_id[self._factory_results.parents]

    async def _save_new_records(self) -> None:
        if new_records := await self._get_unique_records():
            await crud.add_instances(new_records, self._db_session)

    async def _get_unique_records(self) -> Generator[PriceLine, None, None] | None:
        records = set(
            self._factory_results.get_records(self._prod_name_to_id)
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

    product_tags: ResultSet[Tag]
    paginator: ResultSet[Tag]
    box: Box
    results: FactoryResults

    def __init__(self, retailer_id: int, url: str) -> None:
        self.retailer_id = retailer_id
        self.url = url

    async def __call__(self, aio_session: aiohttp.ClientSession) -> None:
        self._aio_session = aio_session
        await self._get_page_tags()
        self.prepare_results()
        self._collect_prices()
        await self._get_paginated_content()
        await self.box.add(self.results)

    async def _get_page_tags(self) -> None:
        """Get page data using aio_session for self.url."""
        # TODO: if not self._html:
        product_area = bs(await self._get_page_html(), 'lxml')\
            .find('div', {'class': "catalog-products"})
        self.product_tags = product_area\
            .find_all('div', {'class': "products__item"})
        self.paginator = product_area.find(
            'div', {'class': 'catalog__pagination'}
        ).find_all('a')

    async def _get_page_html(self) -> str | None:
        async with self._aio_session.get(self.url) as rsp:
            if rsp.status != 200:
                #  TODO: add log and email developer here
                print(f'something went wrong while parsing {self.url}...')
                return None
            return await rsp.text()

    def prepare_results(self) -> None:
        self.results = FactoryResults(
            retailer_id=self.retailer_id,
            parents=self.parents,
        )

    @property
    def parents(self) -> Parents:
        first_tag = self.product_tags[0]
        c_name = first_tag.get('data-item_category3')
        s_name = first_tag.get('data-item_category2')
        return (
            c_name if c_name else s_name,
            s_name if c_name else None,
            first_tag.get('data-item_category')
        )

    def _collect_prices(self) -> None:
        for tag in self.product_tags:
            self.results.add_record(
                (tag.get('data-name'),
                 float(tag.get('data-price')),
                 self.get_promo_price(tag))
            )

    @staticmethod
    def get_promo_price(tag: Tag) -> float | None:  # type: ignore
        if promo := tag.find('span', {'class': 'price__discount'}):
            return float(promo.text.strip().removesuffix(' ₴'))

    @property
    def _page_is_paginated(self) -> bool:
        return bool(self._paginator_size)

    @cached_property
    def _paginator_size(self) -> int:  # type: ignore
        for tag in self.paginator[::-1]:
            if tag.attrs.get('aria-label') == 'Next':
                return int(tag.get('href').split('=')[-1])
        return 0

    async def _get_paginated_content(self):
        if not self._page_is_paginated:
            return
        tasks = (self._page_task(url) for url in self._paginated_urls)
        await asyncio.gather(*tasks)

    async def _page_task(self, url: str) -> None:
        """TODO: Try to remove it."""
        self.url = url
        await self._get_page_tags()
        self._collect_prices()

    @property
    def _paginated_urls(self) -> Generator[str, None, None]:
        return (f'{self.url}?page={_}'
                for _ in range(2, self._paginator_size + 1))

    def __repr__(self) -> str:
        return self.url


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
        self.retailer_id = retailer_id
        for tag in u.get_group_tags(home_url):
            self.create_factory(tag)
        if 'discount' in str(self._factories[0]):
            self._factories.popleft()
        return self._factories

    def create_factory(self, tag) -> None:
        self._factories.append(PriceFactory(self.retailer_id, u.get_url(tag)))


class PriceParser:

    factories: deque[PriceFactory]

    async def refresh_prices(self, retailer_name: RetailerName,
                             db_session: Session) -> None:
        self.retailer = await crud.get_ratailer(retailer_name, db_session)
        PriceFactory.box = Box(db_session, await get_parent_id_table(db_session))
        # await PriceFactory.box.create_folder_to_id_table()  # looks ugly...
        self.get_factories()
        while self.factories:
            self._get_next_batch()  # TODO: Convert to property
            async with u.aiohttp_session_maker() as aio_session:
                tasks = (self.single_factory_task(factory, aio_session)
                         for factory in self._factory_batch)
                await self._complete_tasks(tasks)

    def get_factories(self) -> None:
        self.factories = FactoryCreator()(self.retailer.home_url,
                                          self.retailer.id)

    def _get_next_batch(self) -> None:
        self._factory_batch = {self.factories.pop()
                               for _ in range(self.batch_size)}

    @property
    def batch_size(self) -> int:
        return c.TAVRIA_FACTORIES_PER_SESSION\
            if c.TAVRIA_FACTORIES_PER_SESSION\
            <= len(self.factories)\
            else len(self.factories)

    async def single_factory_task(self, factory: PriceFactory,
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
                self.factories.extend(self._factory_batch)
