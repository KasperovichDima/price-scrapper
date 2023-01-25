import asyncio
from functools import cached_property, lru_cache
import reprlib
from typing import Generator, Mapping
from sqlalchemy.orm import Session
from catalog.models import Folder, Product
import crud
from base_models import BaseWithID
from project_typing import ElType
from .tavria_typing import ObjectParents
import itertools
import aiohttp
from bs4 import BeautifulSoup as bs
from bs4 import ResultSet
from bs4.element import Tag
from fastapi import HTTPException
from .parent_table import ParentTable

class Factory:

    _create_class: type[BaseWithID]
    _aio_session: aiohttp.ClientSession
    _db_session: Session

    _new_objects: list[BaseWithID]
    _parent_content: list[BaseWithID]

    _html: str

    parent_table: Mapping[ObjectParents, int]

    def __init__(self,
                 el_type: ElType,
                 url: str | None = None,
                 category_name: str | None = None,
                 subcategory_name: str | None = None,
                 group_name: str | None = None) -> None:

        self._el_type = el_type
        self._object_names: list[str] = []
        self._url = url
        self._category_name = category_name
        self._subcategory_name = subcategory_name
        self._group_name = group_name
        self._create_class = Product if el_type is ElType.PRODUCT else Folder

    async def __call__(self, **kwargs) -> None:
        self._db_session = kwargs['db_session']
        await self.get_parent_content()
        # await self._refresh_parent_table()
        # 1. take data from page by url
        if 'aio_session' in kwargs:
            self._aio_session = kwargs['aio_session']
            await self._get_page_data()
            if self.__page_is_paginated:
                await self.get_paginated_content()
        # 2. get db objects
        # done in property
        # 3. make actualization
        await self._get_new_objects()
        await self._actualize()
        await self._save_objects()

    def add_name(self, name: str) -> None:
        self._object_names.append(name)

    async def get_parent_content(self) -> None:
        if self _el_type
        self. _parent_content = await crud.get_elements(
            self._create_class,
            self._db_session,
            el_type=[self._el_type]
        )

    async def _get_page_data(self) -> None:
        """Get page data using aio_session if _url is specified."""
        await self.get_page_html()
        a_tags: ResultSet[Tag] = bs(self._html, 'lxml').find_all('a')
        tag_names = (self.__get_tag_name(_)
                         for _ in a_tags if self.__get_tag_name(_))
        self._object_names.extend(tag_names)  # type: ignore

    async def get_page_html(self) -> None:
        assert self._url  # TODO: remove
        async with self._aio_session.get(self._url) as response:
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
        # for tag in reversed(paginator):
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
        tasks = (self.page_task(_) for _ in self.__paginated_urls)
        await asyncio.gather(*tasks)

    async def page_task(self, url: str) -> None:
        """TODO: Try to remove it."""
        self._url = url
        await self._get_page_data()

    @property
    def __paginated_urls(self) -> Generator[str, None, None]:
        return (f'{self._url}?page={_}'
                for _ in range(2, self.paginator_size + 1))

    async def _get_new_objects(self):
        in_db_names = set(_.name for _ in await self._parent_content)
        self._new_objects = [self._create_class(name=_,
                                          parent_id=self._parent_id,
                                          el_type=self._el_type)
                       for _ in self._object_names if _ not in in_db_names]

    async def _actualize(self) -> None:
        actual_objects = []
        deprecated_objects = []
        for _ in await self._parent_content:
            actual_objects.append(_) if not _.deprecated else deprecated_objects.append(_)

        to_undeprecate = (_ for _ in deprecated_objects if _.name in self._object_names)
        to_deprecate = (_ for _ in actual_objects if _.name not in self._object_names)

        #  TODO: add if
        for _ in list(itertools.chain(to_undeprecate, to_deprecate)):
            _.deprecated = not _.deprecated
        self._db_session.commit()

    # @property
    # async def _parent_content(self) -> list[BaseWithID]:
    #     try:
    #         self.__parent_content
    #     except AttributeError:
    #         self.__parent_content = await crud.get_elements(self._create_class,
    #                                                         self._db_session,
    #                                                         el_type=[self._el_type])
    #     return self.__parent_content

    @cached_property
    def _parent_id(self) -> int | None:
        if not self._parents:
            return None
        return ParentTable.__parent_table[self._parents]

    @cached_property
    def _parents(self) -> ObjectParents:   
        """TODO: rename grand_parent_name to gp_name, parent_name to p_name"""
        if self._group_name:
            gp_name = self._subcategory_name if self._subcategory_name else self._category_name
            return ObjectParents(gp_name=gp_name, p_name=self._group_name)
        else:
            p_name = self._subcategory_name if self._subcategory_name else self._category_name
            gp_name = self._category_name if self._subcategory_name else None
            return ObjectParents(gp_name=gp_name, p_name=p_name)

    async def _save_objects(self) -> None:
        await crud.add_instances(self._new_objects, self._db_session)
        if self._el_type is not ElType.PRODUCT:
            # self.__parent_content.extend(self._new_objects)  # TODO: Not safe!

    def __repr__(self) -> str:
        return (f'{self._el_type.name}: '
                f'{reprlib.repr(self._object_names)}')
