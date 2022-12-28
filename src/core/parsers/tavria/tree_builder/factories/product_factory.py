"""Product factory class."""
import asyncio
from functools import cached_property
from typing import Iterable

import aiohttp

from catalog.models import Product

from bs4 import BeautifulSoup as bs
from bs4.element import Tag
from bs4 import ResultSet

from fastapi import HTTPException

from .base_factory import BaseFactory
from .....constants import TAVRIA_URL
from .....core_typing import ObjectParents


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

        # return bs(html, 'lxml').find('div', {'class': 'catalog-products'})

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

    async def get_objects(self, session: aiohttp.ClientSession) -> str:
        html = await self.get_page_html(self.url, session)
        self.object_names = self.get_object_names(html)
        if paginated_page_count := self.get_paginated_page_count(html):
            paginated_names = await self.get_paginated_content(paginated_page_count, session)
            self.object_names.extend(paginated_names)
        # for tag in page_tags:
        #     name = tag.text.strip()
        #     if 'product' in tag.get('href') and name:
        #         self.object_names.append(name)
        print(self.object_names)
        # product_area = self.get_product_area(html)
        # product_area: Iterable[Tag] = bs(html, 'lxml').find('div', {'class': 'catalog-products'})
        # tags: ResultSet = product_area.find_all('a')
        # get paginated content
        
            # for page_num in range(2, number_of_pages + 1):
            # jobs = [self.get_page_html(f'{self.full_url}?page={_}', session) for _ in range(2, number_of_pages + 1)]
            # add_html = await asyncio.gather(*jobs)
            # pass

        #         url = f'{self.full_url}?page={page_num}'
        #         html = await self.scrap_page(url, session)
        #         product_area = bs(html, 'lxml').find('div', {'class': 'catalog-products'})
        #         tags.append(product_area.find_all('a'))

            
        # return self.object_names
                



            


        # response = requests.get(self.full_url)
        # if response.status_code != 200:
        #     return
        # print(f'Factory {self.group_name} got rsp from {self.full_url}')
        # return

        # html = bs(response.text, 'lxml')
        # self.object_names = (_.text.strip() for _ in html.find_all('a') if tag_is_product(_))
        # objects = (Product)
        # if not self.__page_is_paginated:
        #     return objects
        # paginated_final_tag = html.find('a', {'aria-label': 'Next'})
        # paginated_href = paginated_final_tag.get('href')
        # count_slice = slice(paginated_href.find('=') + 1, None)
        # paginated_count = int(paginated_href[count_slice])
        # paginated_urls = (f'{self.full_url}/?page={_}' for _ in range(2, paginated_count))
        # async for url in paginated_urls:
        #     async with session.get(url) as response:
        #         pass

    @property
    def _parent_id(self) -> int:
        gp_name = self.subcategory_name if self.subcategory_name\
            else self.category_name
        parents = ObjectParents(grand_parent_name=gp_name,
                                parent_name=self.group_name)
        return self.parents_to_id_table[parents]

    # @cached_property
    # def full_url(self) -> str:
    #     return f'{TAVRIA_URL}{self.url}'



    # @property
    # def __parents(self) -> ObjectParents:
    #     return ObjectParents(
    #         grand_parent_name=self.subcategory_name
    #         if self.subcategory_name else self.category_name,
    #         parent_name=self.group_name
    #     )

    # def get_objects(self) -> str:
    #     parent_id = folders[ObjectParents(self.subcategory_name, self.group_name)]
    #     return

    #     cat_id = next(_.id for _ in folders if _.name == self.category_name)
    #     if self.subcategory_name:
    #         subcat_id = next(_.id for _ in folders if _.name == self.subcategory_name and _.parent_id == cat_id)
    #     group_parent_id = subcat_id if self.subcategory_name else cat_id
    #     parent_id = next(_.id for _ in folders if _.name == self.group_name and _.parent_id == group_parent_id)
    #     return (Product(name=_.name, parent_id=parent_id)
    #             for _ in self.object_names)
