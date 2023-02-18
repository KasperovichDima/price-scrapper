"""Factory and FactoryResults classes."""
import asyncio
from collections import deque
from decimal import Decimal
from functools import cache, cached_property
from typing import Generator, Iterator

import aiohttp

from bs4 import BeautifulSoup as bs
from bs4 import ResultSet, Tag

from exceptions import EqCompareError

from parsers import exceptions as e

from project_typing import PriceRecord

from .product_box import product_box
from .tavria_typing import NameRetailPromo, Path


class FactoryResults:
    """Represents Price factory work
    results with get_records method."""

    __slots__ = ('retailer_id', 'parents', 'records')

    def __init__(self, retailer_id: int) -> None:
        self.retailer_id = retailer_id
        self.parents: Path | None = None
        self.records: deque[NameRetailPromo] = deque()

    def add_record(self, record: NameRetailPromo) -> None:
        self.records.append(record)

    def get_price_lines(self, prod_name_to_id_table: dict[str, int]
                        ) -> set[PriceRecord]:
        """
        Returns tuples:
        (product_id, retailer_id, retail_price, promo_price)
        """

        return set(zip(
            (prod_name_to_id_table[rec[0]] for rec in self.records),
            (self.retailer_id for _ in self.records),
            (rec[1] for rec in self.records),
            (rec[2] for rec in self.records),
            strict=True
        ))


class ProductFactory:

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
            self._collect_prices()
            self._results.parents = self.parents
            await self._get_paginated_content()
            await product_box.add(self._results)
        except Exception as e:
            print(f'Unsuccessful attempt to get data from {self._url}\n'
                  f'Failed with "{e.__class__.__name__}, {e}"')
            return

    async def _get_page_tags(self) -> None:
        """TODO: Add loginfo here!"""
        print(f'Getting data from {self._url}')
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
    def parents(self) -> Path:
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
                 Decimal(tag.get('data-price')),
                 self._get_promo_price(tag))
            )

    @staticmethod
    def _get_promo_price(tag: Tag) -> Decimal | None:  # type: ignore
        if promo := tag.find('span', {'class': 'price__discount'}):
            return Decimal(promo.text.strip().removesuffix(' ₴'))

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
        await self._get_page_tags()
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
        try:
            return self._main_url == __o._main_url  # type: ignore
        except AttributeError:
            raise EqCompareError(self, __o)
