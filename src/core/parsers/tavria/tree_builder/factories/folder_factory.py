"""Folder factory class."""
from functools import cached_property

from project_typing import ElType

from .base_factory import BaseFactory
from ...tavria_typing import ObjectParents


class CategoryFactory(BaseFactory):

    _creating_type = ElType.CATEGORY


class SubcategoryFactory(BaseFactory):
    """TODO: category name to _"""

    _creating_type = ElType.SUBCATEGORY

    def __init__(self, category_name: str, **kwargs) -> None:

        if not category_name:
            raise TypeError
            
        self.category_name = category_name
        super().__init__()

    @cached_property
    def _parent_id(self) -> int:
        parents = ObjectParents(grand_parent_name=None,
                                parent_name=self.category_name)
        return self._parents_to_id_table[parents]


class GroupFactory(BaseFactory):
    """TODO: category and subcategory name to _"""

    _creating_type = ElType.GROUP

    def __init__(self, category_name: str,
                 subcategory_name: str | None = None, **kwargs) -> None:
        
        if not category_name:
            raise TypeError

        self.category_name = category_name
        self.subcategory_name = subcategory_name
        super().__init__()

    @cached_property
    def _parent_id(self) -> int:
        grandparent = self.category_name if self.subcategory_name else None
        parent = self.subcategory_name if self.subcategory_name\
            else self.category_name
        return self._parents_to_id_table[ObjectParents(grandparent, parent)]
