"""Tavria price parser."""
from __future__ import annotations

import asyncio
from collections import deque
from functools import cached_property
from typing import Generator, Iterable, NamedTuple

import aiohttp

from bs4 import BeautifulSoup as bs
from bs4 import ResultSet, Tag 

from catalog.models import Product

from core.models import PriceLine

import crud

from project_typing import ElType, RetailerName
from project_typing import PriceRecord

from sqlalchemy.orm import Session

from . import constants as c
from . import utils as u
from .tavria_typing import Parents


class FactoryResults(NamedTuple):
    """TODO: Convert to pydantic?"""
    retailer_id: int
    parents: Parents
    names: Iterable[str]
    retail_prices: Iterable[float]
    promo_prices: Iterable[float | None]

    def get_records(
        self, prod_name_to_id_table: dict[str, int]
    ) -> Iterable[PriceRecord]:
        """
        Returns tuples:
        (product_id, retailer_id, retail_price, promo_price)
        """
        return zip(
            (prod_name_to_id_table[name] for name in self.names),
            (self.retailer_id for _ in self.names),
            self.retail_prices,
            self.promo_prices,
            strict=True
        )


class Box:

    # folder_id: int

    folder_to_id_table: dict[Parents, int] = {}  # TODO: naming
    # group_id: int
    retailer_id: int
    last_price_lines: list[PriceLine]
    prod_name_to_id_table: dict[str, int]

    # factory_class = PriceLine  # TODO: Make dynamic

    factory_results: FactoryResults

    saved_objects: list[PriceLine]  # TODO: Make dynamic
    group_products: list[Product]

    def __init__(self, db_session: Session) -> None:
        self._db_session = db_session

    async def add(self, factory_results: FactoryResults) -> None:
        # 1. get this group id (cached property)
        # 2. get products of this group from db
        # 3. get saved last prices of this group by prod_id
        # 4. convert result products names to ids
        # 5. remove eq from factory results
        # 6. update records, where prices was changed
        # 7. remove them from factory results
        # 8. all left in factory results - are new records.
        # 9. create new price lines for this products.

        self.factory_results = factory_results
        # await self.create_folder_to_id_table()
        await self.get_group_products()
        await self.get_last_price_lines()
        self.create_prod_name_to_id_table()
        await self.save_new_records()
        # self.update_changed_records()
        # self.remove_updated_from_results()
        # self.add_new_records()
        # self.clear()

    async def create_folder_to_id_table(self) -> None:
        folders = await crud.get_folders(self._db_session)
        id_to_folder = {_.id: _ for _ in folders}
        groups = (_ for _ in folders if _.el_type is ElType.GROUP)
        for group in groups:
            p_folder = id_to_folder[group.parent_id]
            gp_folder = id_to_folder.get(p_folder.parent_id)
            c_name = gp_folder.name if gp_folder else p_folder.name
            s_name = p_folder.name if gp_folder else None
            g_name = group.name
            parents = (c_name, s_name, g_name)
            self.folder_to_id_table[parents] = group.id

    @property
    def folder_id(self) -> int:
        return self.folder_to_id_table[self.factory_results.parents]

    async def get_group_products(self) -> None:
        # TODO: Only active?
        self.group_products = await crud.get_products(self._db_session,
                                                      folder_ids=(self.folder_id,))

    async def get_last_price_lines(self) -> None:
        prod_ids = (_.id for _ in self.group_products)
        self.last_price_lines = await crud.get_last_price_lines(
            prod_ids, self.factory_results.retailer_id, self._db_session
        )

    def create_prod_name_to_id_table(self) -> None:
        self.prod_name_to_id_table = {_.name: _.id for _ in self.group_products}

    async def save_new_records(self) -> None:
        new_records = set(self.factory_results.get_records(self.prod_name_to_id_table))
        new_records.difference_update(self.last_price_lines)
        if new_records:
            to_save = (PriceLine.from_tuple(_) for _ in new_records)
            await crud.add_instances(to_save, self._db_session)


class PriceFactory:

    product_tags: ResultSet[Tag]
    parents: Parents
    paginator: ResultSet[Tag]
    box: Box

    def __init__(self, retailer_id: int, url: str) -> None:
        self.retailer_id = retailer_id
        self.url = url
        #  Making dedicated results
        # self.prices: Prices = deque()
        self.names: deque[str] = deque()
        self.retail_prices: deque[float] = deque()  # TODO: Convert to array
        self.promo_prices: deque[float | None] = deque()  # TODO: Convert to array

    async def __call__(self, aio_session: aiohttp.ClientSession) -> None:
        self._aio_session = aio_session
        await self._get_page_tags()
        self._set_parents()
        self._collect_prices()
        await self._get_paginated_content()
        await self.box.add(self.collect_results())

    async def _get_page_tags(self) -> None:
        """Get page data using aio_session if _url is specified."""
        # TODO: if not self._html:
        product_area = bs(await self._get_page_html(), 'lxml')\
            .find('div', {'class': "catalog-products"})
        self.product_tags = product_area\
            .find_all('div', {'class': "products__item"})
        self.paginator = product_area.find('div', {'class': 'catalog__pagination'}).find_all('a')

    async def _get_page_html(self) -> str | None:
        """TODO: This function should return html."""

        async with self._aio_session.get(self.url) as rsp:  # type: ignore
            if rsp.status != 200:
                #  TODO: add log and email developer here
                print(f'something went wrong while parsing {self.url}...')
                return None
            return await rsp.text()

    def _set_parents(self) -> None:
        tag = self.product_tags[0]
        c_name = tag.get('data-item_category3')
        s_name = tag.get('data-item_category2')
        self.parents = (
            c_name if c_name else s_name,
            s_name if c_name else None,
            tag.get('data-item_category')
        )
        # self.parents = Parents(
        #     category_name=c_name if c_name else s_name,
        #     subcategory_name=s_name if c_name else None,
        #     group_name=tag.get('data-item_category')
        # )

    def _collect_prices(self) -> None:
        for tag in self.product_tags:
            self.names.append(tag.get('data-name'))
            self.retail_prices.append(float(tag.get('data-price')))
            self.promo_prices.append(self.get_discount_price(tag))

    @staticmethod
    def get_discount_price(tag: Tag) -> float | None:  # type: ignore
        if discount := tag.find('span', {'class': 'price__discount'}):
            return float(discount.text.strip().removesuffix(' ₴'))

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
        tasks = (self._page_task(_) for _ in self._paginated_urls)
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

    def collect_results(self) -> FactoryResults:
        return FactoryResults(self.retailer_id, self.parents, self.names,
                              self.retail_prices, self.promo_prices)


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
        PriceFactory.box = Box(db_session)
        await PriceFactory.box.create_folder_to_id_table()  # looks ugly...
        self.get_factories()
        while self.factories:
            self._get_next_batch()  # TODO: Convert to property
            async with u.aiohttp_session_maker() as aio_session:
                tasks = (self.single_factory_task(factory, aio_session)
                         for factory in self._factory_batch)
                await self._complete_tasks(tasks)

    def get_factories(self) -> None:
        self.factories = FactoryCreator()(self.retailer.home_url, self.retailer.id)

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


from .tests.html import groups_v2 as g

mocked_pages: dict[str, str] = dict(
    catalog_buckwheat=g.catalog_buckwheat,
    catalog_corn=g.catalog_corn,
    catalog_rice=g.catalog_rice,
    catalog_protein=g.catalog_protein,
    catalog_fast_food=g.catalog_fast_food,
    catalog_chips=g.catalog_chips,
)
mocked_pages['catalog_rice?page=2'] = g.catalog_rice_2
mocked_pages['catalog_rice?page=3'] = g.catalog_rice_3


class PriceFactory_test(PriceFactory):
    """Mock class for testing with changed _get_page_html method"""

    async def _get_page_html(self) -> str | None:
        return mocked_pages[self.url]


class FactoryCreator_test(FactoryCreator):
    """Mock class for testing with changed create_factory method."""

    def create_factory(self, tag) -> None:
        """Should use PriceFactory_test class instead of PriceFactory."""
        self._factories.append(PriceFactory_test(self.retailer_id, u.get_url(tag)))


class PriceParser_test(PriceParser):
    """Mock class for testing with changed get_factories method."""

    def get_factories(self) -> None:
        """Should use FactoryCreator_test class instead of FactoryCreator."""
        self.factories = FactoryCreator_test()(self.retailer.home_url, self.retailer.id)
