"""Product factory class."""
import requests

from bs4 import BeautifulSoup as bs
from bs4.element import Tag

from catalog.models import Product

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

    async def get_objects(self) -> str:
        response = requests.get(self.full_url)
        if response.status_code != 200:
            return
        print(f'Factory {self.group_name} got rsp from {self.full_url}')
        return
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

    def __page_is_paginated(self) -> bool:
        return False

    @property
    def _parent_id(self) -> int:
        gp_name = self.subcategory_name if self.subcategory_name\
            else self.category_name
        parents = ObjectParents(grand_parent_name=gp_name,
                                parent_name=self.group_name)
        return self.parents_to_id_table[parents]

    @property
    def full_url(self) -> str:
        return f'{TAVRIA_URL}{self.url}'



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
