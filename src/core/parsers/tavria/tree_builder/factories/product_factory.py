"""Product factory class."""
import asyncio
from functools import cached_property
from typing import Iterable

import aiohttp

from bs4 import BeautifulSoup as bs
from bs4.element import Tag

from catalog.models import Product

from fastapi import HTTPException

from .base_factory import BaseFactory
from ...tavria_typing import BaseFactoryReturnType
from ...tavria_typing import ObjectParents


def tag_is_product(tag: Tag) -> bool:
    return ('product' in tag.get('href'))


class ProductFactory(BaseFactory):

    url: str
    category_name: str
    subcategory_name: str | None = None
    group_name: str

    def __bool__(self) -> bool:
        return all((self.url, self.category_name, self.group_name))

    async def get_page_html(self, url: str, session: aiohttp.ClientSession) -> str:
        print(url, 'is in progress...')
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(503, f'Error while parsing {self.url}')
            return await response.text()

    def get_object_names(self, html: str) -> bs:
        a_tags: Iterable[Tag] = bs(html, 'lxml').find_all('a')
        return [_.text.strip() for _ in a_tags if 'product' in _.get('href', '') and not _.text.isspace()]

    def get_paginated_page_count(self, html: str) -> int:
        if not (paginator := self.get_paginator(html)):
            return 0
        for tag in reversed(paginator):
            try:
                assert tag.attrs['aria-label'] == 'Next'
                return int(tag.get('href').split('=')[-1])
            except (AssertionError, KeyError):
                continue

    def get_paginator(self, html: str):
        return bs(html, 'lxml').find('div', {'class': 'catalog__pagination'}).find_all('a')

    async def get_paginated_content(self, page_count: int, session: aiohttp.ClientSession):
        urls = (f'{self.url}?page={_}' for _ in range(2, page_count + 1))
        jobs = [self.get_page_html(_, session) for _ in urls]
        paginated_pages_html = await asyncio.gather(*jobs)
        res = []
        for _ in paginated_pages_html:
            res.extend(self.get_object_names(_))
        return res

    async def get_objects(self, session: aiohttp.ClientSession) -> BaseFactoryReturnType:
        html = await self.get_page_html(self.url, session)
        self.object_names = self.get_object_names(html)
        if paginated_page_count := self.get_paginated_page_count(html):
            paginated_names = await self.get_paginated_content(paginated_page_count, session)
            self.object_names.extend(paginated_names)
        return (Product(name=name, parent_id=self._parent_id) for name in self.object_names)

    @cached_property
    def _parent_id(self) -> int:
        gp_name = self.subcategory_name if self.subcategory_name\
            else self.category_name
        parents = ObjectParents(grand_parent_name=gp_name,
                                parent_name=self.group_name)
        return self.parents_to_id_table[parents]
