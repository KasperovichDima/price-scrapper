"""Factory and FactoryResults classes."""
import asyncio
import traceback
from collections import deque
from decimal import Decimal
from functools import cached_property
from typing import Generator

import aiohttp

from bs4 import BeautifulSoup as bs
from bs4 import ResultSet, Tag

from exceptions import EqCompareError

from parsers import exceptions as e

from project_typing import NameRetailPromo

from .result_box import save_results
from .support_classes import FactoryResults
from .tavria_typing import Path


class ProductFactory:

    """ProductFactory collects product names and prices from specified page
    and pages's paginated content. Then send them to product box, where they
    will be processed and saved. Provides 'run' method to start factory.
    aio_session needed."""

    _product_tags: ResultSet[Tag]
    _records: deque[NameRetailPromo]

    __PARSER_ERROR_MSG = """
    Error while getting response from {}...
    """

    def __init__(self, url: str) -> None:
        self._main_url = self._url = url
        self._records: deque[NameRetailPromo] = deque()

    async def run(self, aio_session: aiohttp.ClientSession) -> None:
        # TODO: Add loginfo here
        self._aio_session = aio_session
        try:
            await self._get_page_tags()
            self._collect_prices()
            await self._get_paginated_content()
            await save_results(FactoryResults(self._parent_path,
                                              self._records))

        except Exception as e:
            print('*' * 60)
            print(f'Unsuccessful attempt for {self._url}\n'
                  f'Failed with "{e.__class__.__name__}, \n{e}"')
            traceback.print_tb(e.__traceback__, -3)
            print('*' * 60)

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
                raise e.UnexpectedParserException(
                    self.__PARSER_ERROR_MSG.format(self._url)
                )
            return await rsp.text()

    def _get_product_tags(self) -> None:
        self._product_tags = self._product_area\
            .find_all('div', {'class': "products__item"})

    @property
    def _parent_path(self) -> Path:
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
            self._records.append(
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
