"""Folder and Product factory class + base class."""
import asyncio
import reprlib
from collections.abc import Mapping
from functools import cached_property, lru_cache
from typing import Generator

import aiohttp

from bs4 import BeautifulSoup as bs
from bs4 import ResultSet
from bs4.element import Tag

from catalog.models import BaseCatalogElement, Folder, Product

from fastapi import HTTPException

from project_typing import ElType

from .tavria_typing import BaseFactoryReturnType
from .tavria_typing import ObjectParents
from ..exceptions import EmptyFactoryDataError


class BaseFactory:
    """Contains all required information for catalog objects
    cretion. Creates objects using create_objects method."""

    _creating_type: ElType
    _creating_class: type[BaseCatalogElement] = Folder
    parent_table: Mapping[ObjectParents, int]

    def __init__(self, **kwargs) -> None:
        self._validate_init_data()
        self._object_names: list[str] = []

    def add_name(self, name: str) -> None:
        self._object_names.append(name)

    def get_objects(self, *args) -> BaseFactoryReturnType:
        """
        Create and return factory objects. Template method.
        TODO: Check speed with async.
        """

        return (self._creating_class(name=name,
                                     parent_id=self._parent_id,
                                     el_type=self._creating_type)
                for name in self._object_names)

    def _validate_init_data(self) -> None:
        """Validates init data. Raises EmptyFactoryDataError
        if required data miss or is empty."""
        raise EmptyFactoryDataError('Some of init data args are empty.')

    @cached_property
    def _parent_id(self) -> int | None: ...

    def __bool__(self) -> bool:
        return bool(self._object_names)

    def __repr__(self) -> str:
        return (f'{self._creating_type.name}: '
                f'{reprlib.repr(self._object_names)}')


class CategoryFactory(BaseFactory):

    _creating_type = ElType.CATEGORY

    def _validate_init_data(self) -> None:
        pass


class SubcategoryFactory(BaseFactory):

    _creating_type = ElType.SUBCATEGORY

    def __init__(self, category_name: str, **kwargs) -> None:
        self._category_name = category_name
        super().__init__()

    def _validate_init_data(self) -> None:
        if self._category_name:
            return
        super()._validate_init_data()

    @cached_property
    def _parent_id(self) -> int:
        parents = ObjectParents(grand_parent_name=None,
                                parent_name=self._category_name)
        return self.parent_table[parents]


class GroupFactory(BaseFactory):

    _creating_type = ElType.GROUP

    def __init__(self, category_name: str,
                 subcategory_name: str | None = None, **kwargs) -> None:
        self._category_name = category_name
        self._subcategory_name = subcategory_name
        super().__init__()

    def _validate_init_data(self) -> None:
        if self._category_name and self._subcategory_name != '':
            return
        super()._validate_init_data()

    @cached_property
    def _parent_id(self) -> int:
        gp_name = self._category_name if self._subcategory_name else None
        p_name = self._subcategory_name if self._subcategory_name\
            else self._category_name
        return self.parent_table[ObjectParents(gp_name, p_name)]


class ProductFactory(BaseFactory):

    _creating_type = ElType.PRODUCT

    __session: aiohttp.ClientSession
    _html: str

    def __init__(self, url: str, category_name: str, group_name: str,
                 subcategory_name: str | None = None, **kwargs) -> None:
        self._url = url
        self._category_name = category_name
        self.group_name = group_name
        self._subcategory_name = subcategory_name
        super().__init__()

    def _validate_init_data(self) -> None:
        if (all((self._url, self._category_name,
           self.group_name, self._subcategory_name != ''))):
            return
        super()._validate_init_data()

    async def get_objects(self, session: aiohttp.ClientSession
                          ) -> BaseFactoryReturnType:
        self.__session = session
        await self.scrap_object_names()
        if self.__page_is_paginated:
            await self.get_paginated_content()

        return (Product(name=name, parent_id=self._parent_id)
                for name in self._object_names)

    async def scrap_object_names(self) -> None:
        await self.get_page_html()
        a_tags: ResultSet[Tag] = bs(self._html, 'lxml').find_all('a')
        correct_names = (self.__get_product_name(_)
                         for _ in a_tags if self.__get_product_name(_))
        self._object_names.extend(correct_names)  # type: ignore

    @staticmethod
    @lru_cache(1)
    def __get_product_name(tag: Tag) -> str | None:
        """Returns a name of product, if tag contains it."""
        return tag.text.strip()\
            if 'product' in tag.get('href', '')\
            and not tag.text.isspace() else None

    async def get_page_html(self) -> None:
        async with self.__session.get(self._url) as response:
            if response.status != 200:
                raise HTTPException(503, f'Error while parsing {self._url}')
                #  TODO: add log and email developer here
            self._html = await response.text()

    @property
    def __page_is_paginated(self) -> bool:
        return bool(self.paginator_size)

    @cached_property
    def paginator_size(self) -> int:  # type: ignore
        """TODO: try to Remove paginator := self.paginator."""
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
        return bs(self._html, 'lxml')\
            .find('div', {'class': 'catalog__pagination'}).find_all('a')

    async def get_paginated_content(self):
        jobs = (self.page_task(_) for _ in self.__paginated_urls)
        await asyncio.gather(*jobs)

    @property
    def __paginated_urls(self) -> Generator[str, None, None]:
        return (f'{self._url}?page={_}'
                for _ in range(2, self.paginator_size + 1))

    async def page_task(self, url: str) -> None:
        self._url = url
        await self.scrap_object_names()

    @cached_property
    def _parent_id(self) -> int:
        grand_parent_name = self._subcategory_name\
            if self._subcategory_name else self._category_name
        parents = ObjectParents(grand_parent_name=grand_parent_name,
                                parent_name=self.group_name)
        return self.parent_table[parents]

    def __bool__(self) -> bool:
        return all((self._url, self._category_name, self.group_name))
