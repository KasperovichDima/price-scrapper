""""""
from collections import deque
from collections.abc import Mapping
from typing import ClassVar

from catalog.models import Folder, Product

from project_typing import ElType

from pydantic import BaseModel, Field

from ...core_typing import BaseFactoryReturnType
from ...core_typing import FolderParents
from ...core_typing import FolderReturnType


class BaseFactory(BaseModel):
    """Contains all required information for catalog objects
    cretion. Creates objects using create_objects method."""

    parent_to_id_table: ClassVar[Mapping[FolderParents, int]]

    object_names: deque[str] = Field(default_factory=deque)

    def __bool__(self) -> bool:
        return bool(self.object_names)

    def add_name(self, name: str) -> None:
        self.object_names.append(name)

    def get_objects(self) -> BaseFactoryReturnType: ...

    class Config:
        arbitrary_types_allowed = True


class CategoryFactory(BaseFactory):

    def get_objects(self) -> FolderReturnType:
        return (Folder(name=_, el_type=ElType.CATEGORY)
                for _ in self.object_names)


class SubcategoryFactory(BaseFactory):

    category_name: str

    def get_objects(self) -> FolderReturnType:
        parent_id = self.parent_to_id_table[FolderParents(None,
                                            self.category_name)]
        return (Folder(name=name,
                       parent_id=parent_id,
                       el_type=ElType.SUBCATEGORY)
                for name in self.object_names)


class GroupFactory(BaseFactory):

    category_name: str
    subcategory_name: str | None = None

    def get_objects(self) -> FolderReturnType:
        return (Folder(name=name,
                       parent_id=self.parent_to_id_table[self.__key],
                       el_type=ElType.GROUP)
                for name in self.object_names)

    @property
    def __key(self) -> FolderParents:
        return FolderParents(self.category_name, self.subcategory_name)\
            if self.subcategory_name\
            else FolderParents(None, self.category_name)


class ProductFactory(BaseFactory):

    url: str
    category_name: str
    subcategory_name: str | None = None
    group_name: str

    def __bool__(self) -> bool:
        return all((self.url, self.category_name, self.group_name))

    def get_objects(self) -> BaseFactoryReturnType:
        parent_id = folders[FolderParents(self.subcategory_name, self.group_name)]
        return

        cat_id = next(_.id for _ in folders if _.name == self.category_name)
        if self.subcategory_name:
            subcat_id = next(_.id for _ in folders if _.name == self.subcategory_name and _.parent_id == cat_id)
        group_parent_id = subcat_id if self.subcategory_name else cat_id
        parent_id = next(_.id for _ in folders if _.name == self.group_name and _.parent_id == group_parent_id)
        return (Product(name=_.name, parent_id=parent_id)
                for _ in self.object_names)


__FACTORIES_TYPES: dict[ElType, type[BaseFactory]] = {
    ElType.CATEGORY: CategoryFactory,
    ElType.SUBCATEGORY: SubcategoryFactory,
    ElType.GROUP: GroupFactory,
    ElType.PRODUCT: ProductFactory
}


def get_factory_class(type_: ElType):
    """Get factory by element type."""
    return __FACTORIES_TYPES[type_]
