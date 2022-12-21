""""""
from collections import deque

from typing import Iterable

from catalog.models import Folder, Product

from interfaces import ICatalogElement

from project_typing import ElType

from pydantic import BaseModel


class CatalogFactory(BaseModel):
    """Contains all required information for catalog objects
    cretion. Creates objects using create_objects method."""

    object_names: deque[str] = deque()

    def __bool__(self) -> bool:
        return bool(self.object_names)

    def add_name(self, name: str) -> None:
        self.object_names.append(name)

    def get_objects(self, folders: Iterable[Folder]) -> Iterable[ICatalogElement]:
        ...


class CategoryFactory(CatalogFactory):

    def get_objects(self, folders: Iterable[Folder]) -> Iterable[Folder]:
        return (Folder(name=_, type=ElType.CATEGORY) for _ in self.object_names)

    
class SubcategoryFactory(CatalogFactory):

    category_name: str

    def get_objects(self, folders: Iterable[Folder]) -> Iterable[Folder]:
        parent_id: int = next(_.id for _ in folders if _.name == self.category_name)
        return (Folder(name=name,
                       parent_id=parent_id,
                       type=ElType.SUBCATEGORY)
                for name in self.object_names)


class GroupFactory(CatalogFactory):

    category_name: str
    subcategory_name: str | None = None

    def get_objects(self, folders: Iterable[Folder]) -> Iterable[Folder]:
        cat_id = next(_.id for _ in folders if _.name == self.category_name)
        if self.subcategory_name:
            parent_id = next(_.id for _ in folders if _.name == self.subcategory_name and _.parent_id == cat_id)
        return (Folder(name=name,
                       parent_id=parent_id if self.subcategory_name else cat_id,
                       type=ElType.GROUP)
                for name in self.object_names)


class ProductFactory(CatalogFactory):

    url: str
    category_name: str
    subcategory_name: str | None = None
    group_name: str

    def __bool__(self) -> bool:
        return all((self.url, self.category_name, self.group_name))

    def get_objects(self, folders: Iterable[Folder]) -> Iterable[ICatalogElement]:

        return

        cat_id = next(_.id for _ in folders if _.name == self.category_name)
        if self.subcategory_name:
            subcat_id = next(_.id for _ in folders if _.name == self.subcategory_name and _.parent_id == cat_id)
        group_parent_id = subcat_id if self.subcategory_name else cat_id
        parent_id = next(_.id for _ in folders if _.name == self.group_name and _.parent_id == group_parent_id)
        return (Product(name=_.name, parent_id=parent_id)
                for _ in self.object_names)


__FACTORIES: dict[ElType, type[CatalogFactory]] = {
    ElType.CATEGORY: CategoryFactory,
    ElType.SUBCATEGORY: SubcategoryFactory,
    ElType.GROUP: GroupFactory,
    ElType.PRODUCT: ProductFactory
}


def get_factory_class(type_: ElType):
    """Get factory by element type."""
    return __FACTORIES[type_]
