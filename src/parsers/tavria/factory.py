import asyncio
import reprlib
from functools import cached_property, lru_cache
from typing import Generator

import aiohttp

from bs4 import BeautifulSoup as bs
from bs4 import ResultSet
from bs4.element import Tag

from catalog.utils import get_class_by_type

from parsers.exceptions import UnexpectedParserError

from project_typing import ElType

from .object_box import ObjectBox
from .parent_table import ParentTable
from .tavria_typing import ObjectParents


class BaseFactory:
    """TODO: Correct params order."""

    object_box: ObjectBox

    def __init__(self,
                 el_type: ElType,
                 *args,
                 category_name: str | None = None,
                 subcategory_name: str | None = None,
                 group_name: str | None = None,
                 **kwds) -> None:
        self._el_type = el_type
        self._category_name = category_name
        self._subcategory_name = subcategory_name
        self._group_name = group_name
        self._object_names: list[str] = []
        assert self.object_box

    async def __call__(self, *args, **kwds) -> None:
        """TODO: Devide on 'pre', 'main_process', 'post'."""
        await self._get_new_objects()

    async def _get_new_objects(self):
        cls_ = get_class_by_type(self._el_type)
        new_objects = (cls_(name=name,
                            parent_id=self._parent_id,
                            el_type=self._el_type)
                       for name in self._object_names)
        await self.object_box.add(new_objects)

    @cached_property
    def _parent_id(self) -> int | None:
        if not self._parents:
            return None
        return ParentTable.get_table()[self._parents]

    @cached_property
    def _parents(self) -> ObjectParents:
        """TODO: rename grand_parent_name to gp_name, parent_name to p_name"""
        if self._group_name:
            gp_name = self._subcategory_name if self._subcategory_name\
                else self._category_name
            return ObjectParents(gp_name=gp_name, p_name=self._group_name)
        else:
            p_name = self._subcategory_name if self._subcategory_name\
                else self._category_name
            gp_name = self._category_name if self._subcategory_name else None
            return ObjectParents(gp_name=gp_name, p_name=p_name)

    def __repr__(self) -> str:
        parent_name = self._subcategory_name if self._subcategory_name\
            else self._category_name
        return (f'{parent_name}: '
                f'{reprlib.repr(self._object_names)}')

    def __bool__(self) -> bool:
        return bool(self._object_names)

    def __hash__(self) -> int:
        return hash((self._el_type,
                     self._category_name,
                     self._subcategory_name,
                     self._group_name))

    def __eq__(self, __o: object) -> bool:
        return hash(self) == hash(__o)

    def __add__(self, name: str) -> None:
        self._object_names.append(name)


class FolderFactory(BaseFactory):

    def add_name(self, name: str) -> None:
        """TODO: Fix interface."""
        self._object_names.append(name)


class ProductFactory(BaseFactory):
    """TODO: Correct params order."""
    _aio_session: aiohttp.ClientSession
    _html: str

    def __init__(self, url: str | None = None, **kwds) -> None:
        self._url = url
        super().__init__(**kwds)

    async def __call__(self, aio_session: aiohttp.ClientSession) -> None:
        self._aio_session = aio_session
        await self._get_page_data()
        if self.__page_is_paginated:
            await self.get_paginated_content()
        await super().__call__()

    async def _get_page_data(self) -> None:
        """Get page data using aio_session if _url is specified."""
        await self.get_page_html()
        # TODO: if not self._html:
        a_tags: ResultSet[Tag] = bs(self._html, 'lxml').find_all('a')
        tag_names = (self.__get_tag_name(_)
                     for _ in a_tags if self.__get_tag_name(_))
        self._object_names.extend(tag_names)  # type: ignore

    async def get_page_html(self) -> None:
        async with self._aio_session.get(self._url) as response:  # type: ignore  # noqa: E501
            if response.status != 200:
                #  TODO: add log and email developer here
                print(f'something went wrong while parsing {self._url}...')
                return
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
        raise UnexpectedParserError

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

    def __repr__(self) -> str:
        return (f'{self._group_name}: '
                f'{reprlib.repr(self._object_names)}')
