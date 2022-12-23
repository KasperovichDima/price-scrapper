"""Product factory class."""
from catalog.models import Product

from .base_factory import BaseFactory
from .....core_typing import FolderParents


class ProductFactory(BaseFactory):

    url: str
    category_name: str
    subcategory_name: str | None = None
    group_name: str

    def __bool__(self) -> bool:
        return all((self.url, self.category_name, self.group_name))

    def get_objects(self) -> str:
        parent_id = folders[FolderParents(self.subcategory_name, self.group_name)]
        return

        cat_id = next(_.id for _ in folders if _.name == self.category_name)
        if self.subcategory_name:
            subcat_id = next(_.id for _ in folders if _.name == self.subcategory_name and _.parent_id == cat_id)
        group_parent_id = subcat_id if self.subcategory_name else cat_id
        parent_id = next(_.id for _ in folders if _.name == self.group_name and _.parent_id == group_parent_id)
        return (Product(name=_.name, parent_id=parent_id)
                for _ in self.object_names)