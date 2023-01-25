import asyncio
from functools import cached_property, lru_cache
from typing import Generator
import aiohttp
from bs4 import BeautifulSoup as bs
from bs4 import ResultSet
from bs4.element import Tag
from fastapi import HTTPException

from .new_base_factory import BaseFactory


class ProductFactory(BaseFactory):
    """TODO: Correct params order."""
    _aio_session: aiohttp.ClientSession
    _html: str

    def __init__(self, url: str | None = None, **kwds) -> None:
        self._url = url
        super().__init__(**kwds)

    async def __call__(self, aio_session: aiohttp.ClientSession, object_box) -> None:
        self._aio_session = aio_session
        self._object_box = object_box
        await self._get_page_data()
        if self.__page_is_paginated:
            await self.get_paginated_content()
        await super().__call__()

    async def _get_page_data(self) -> None:
        """Get page data using aio_session if _url is specified."""
        await self.get_page_html()
        a_tags: ResultSet[Tag] = bs(self._html, 'lxml').find_all('a')
        tag_names = (self.__get_tag_name(_)
                     for _ in a_tags if self.__get_tag_name(_))
        self._object_names.extend(tag_names)  # type: ignore

    async def get_page_html(self) -> None:
        async with self._aio_session.get(self._url) as response:  # type: ignore
            if response.status != 200:
                raise HTTPException(503, f'Error while parsing {self._url}')
                #  TODO: add log and email developer here
            self._html = await response.text()

    @staticmethod
    @lru_cache(1)
    def __get_tag_name(tag: Tag) -> str | None:
        """Returns a name from tag, if tag contains it."""
        return tag.text.strip()\
            if 'product' in tag.get('href', '')\
            and not tag.text.isspace() else None
    
    @property
    def __page_is_paginated(self) -> bool:
        return bool(self.paginator_size)

    @cached_property
    def paginator_size(self) -> int:  # type: ignore
        """TODO: try to Remove paginator := self.paginator."""
        if not (paginator := self.paginator):
            return 0
        for tag in paginator[::-1]:
            try:
                assert tag.attrs['aria-label'] == 'Next'
                return int(tag.get('href').split('=')[-1])
            except (AssertionError, KeyError):
                continue

    @cached_property
    def paginator(self) -> ResultSet:
        return bs(self._html, 'lxml')\
            .find('div', {'class': 'catalog__pagination'}).find_all('a')

    async def get_paginated_content(self):
        tasks = (self.page_task(_) for _ in self._paginated_urls)
        await asyncio.gather(*tasks)

    async def page_task(self, url: str) -> None:
        """TODO: Try to remove it."""
        self._url = url
        await self._get_page_data()

    @property
    def _paginated_urls(self) -> Generator[str, None, None]:
        return (f'{self._url}?page={_}'
                for _ in range(2, self.paginator_size + 1))

    def __bool__(self) -> bool:
        """TODO: Ref! Duplicates with init validation."""
        return all((self._category_name,
                    self._group_name,
                    self._url))
