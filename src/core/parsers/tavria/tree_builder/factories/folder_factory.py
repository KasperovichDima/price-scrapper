"""Folder factory class."""
from catalog.models import Folder

from project_typing import ElType

from .base_factory import BaseFactory
from .....core_typing import FolderParents
from .....core_typing import FolderReturnType


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
