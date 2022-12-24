"""Folder factory class."""
from functools import cached_property

from project_typing import ElType

from .base_factory import BaseFactory
from .....core_typing import ObjectParents


class CategoryFactory(BaseFactory):

    _creating_type = ElType.CATEGORY


class SubcategoryFactory(BaseFactory):

    _creating_type = ElType.SUBCATEGORY
    category_name: str

    @cached_property
    def _parent_id(self) -> int:
        parents = ObjectParents(grand_parent_name=None,
                                parent_name=self.category_name)
        return self.parents_to_id_table[parents]


class GroupFactory(BaseFactory):

    _creating_type = ElType.GROUP
    category_name: str
    subcategory_name: str | None = None

    @cached_property
    def _parent_id(self) -> int:
        grandparent = self.category_name if self.subcategory_name else None
        parent = self.subcategory_name if self.subcategory_name\
            else self.category_name
        return self.parents_to_id_table[ObjectParents(grandparent, parent)]
