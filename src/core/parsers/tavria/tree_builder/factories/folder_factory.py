"""Folder factory class."""
from catalog.models import Folder

from project_typing import ElType

from .base_factory import BaseFactory
from .....core_typing import ObjectParents
from .....core_typing import FolderReturnType


class CategoryFactory(BaseFactory):

    _creating_type = ElType.CATEGORY
    _creating_class = Folder
    _parent_id = None


class SubcategoryFactory(BaseFactory):

    _creating_type = ElType.SUBCATEGORY
    _creating_class = Folder
    category_name: str

    @property
    def _parent_id(self) -> int:
        parents = ObjectParents(None, self.category_name)
        return self.parents_to_id_table[parents]


class GroupFactory(BaseFactory):

    _creating_type = ElType.GROUP
    _creating_class = Folder
    category_name: str
    subcategory_name: str | None = None

    @property
    def _parent_id(self) -> int:
        parents = ObjectParents(self.category_name, self.subcategory_name)\
            if self.subcategory_name\
            else ObjectParents(None, self.category_name)
        return self.parents_to_id_table[parents]
