"""Product factory class."""
import asyncio
from functools import cached_property

import aiohttp

from bs4 import BeautifulSoup as bs
from bs4 import ResultSet
from bs4.element import Tag

from catalog.models import Product

from fastapi import HTTPException

from .base_factory import BaseFactory
from .utils import get_product_name
from ...tavria_typing import BaseFactoryReturnType
from ...tavria_typing import ObjectParents


class ProductFactory(BaseFactory):

    url: str
    category_name: str
    group_name: str
    session: aiohttp.ClientSession | None = None

    html: str | None = None  # TODO: Looks ugly
    subcategory_name: str | None = None

    async def get_objects(self, session: aiohttp.ClientSession
                          ) -> BaseFactoryReturnType:
        # TODO: Make session class var
        self.session = session
        await self.scrap_object_names()
        if self.__page_is_paginated:
            await self.get_paginated_content()

        return (Product(name=name, parent_id=self._parent_id)
                for name in self.object_names)

    async def scrap_object_names(self) -> None:
        await self.get_page_html()
        a_tags: ResultSet[Tag] = bs(self.html, 'lxml').find_all('a')
        correct_names = (get_product_name(_)
                         for _ in a_tags if get_product_name(_))
        self.object_names.extend(correct_names)  # type: ignore

    async def get_page_html(self) -> None:
        async with self.session.get(self.url) as response:
            if response.status != 200:
                raise HTTPException(503, f'Error while parsing {self.url}')
                #  TODO: add log and email developer here
            self.html = await response.text()

    @property
    def __page_is_paginated(self) -> bool:
        return bool(self.paginator_size)

    @cached_property
    def paginator_size(self) -> int:  # type: ignore
        if not (paginator := self.paginator):
            return 0
        for tag in reversed(paginator):
            try:
                assert tag.attrs['aria-label'] == 'Next'
                return int(tag.get('href').split('=')[-1])
            except (AssertionError, KeyError):
                continue

    @cached_property
    def paginator(self) -> ResultSet:
        return bs(self.html, 'lxml')\
            .find('div', {'class': 'catalog__pagination'}).find_all('a')

    async def get_paginated_content(self):
        urls = (f'{self.url}?page={_}'
                for _ in range(2, self.paginator_size + 1))
        jobs = (self.page_task(_) for _ in urls)
        await asyncio.gather(*jobs)

    async def page_task(self, url: str) -> None:
        self.url = url
        await self.scrap_object_names()

    @cached_property
    def _parent_id(self) -> int:
        grand_parent_name = self.subcategory_name\
            if self.subcategory_name else self.category_name
        parents = ObjectParents(grand_parent_name=grand_parent_name,
                                parent_name=self.group_name)
        return self.parents_to_id_table[parents]

    def __bool__(self) -> bool:
        return all((self.url, self.category_name, self.group_name))
