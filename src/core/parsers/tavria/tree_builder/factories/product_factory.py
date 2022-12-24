"""Product factory class."""
import aiohttp

from catalog.models import Product

from .base_factory import BaseFactory
from .....constants import TAVRIA_URL
from .....core_typing import ObjectParents


class ProductFactory(BaseFactory):

    url: str
    category_name: str
    subcategory_name: str | None = None
    group_name: str

    def __bool__(self) -> bool:
        return all((self.url, self.category_name, self.group_name))

    async def get_objects(self) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.full_url) as response:
                if response.status != 200:
                    return
                html = await response.text()

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
