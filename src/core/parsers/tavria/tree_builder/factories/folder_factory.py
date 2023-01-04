"""Folder factory class."""
from functools import cached_property

from project_typing import ElType

from .base_factory import BaseFactory
from ...tavria_typing import ObjectParents


class CategoryFactory(BaseFactory):

    _creating_type = ElType.CATEGORY

    def _validate_init_data(self) -> None:
        pass


class SubcategoryFactory(BaseFactory):
    """TODO: category name to _"""

    _creating_type = ElType.SUBCATEGORY

    def __init__(self, category_name: str, **kwargs) -> None:
        self._category_name = category_name
        super().__init__()

    def _validate_init_data(self) -> None:
        if self._category_name:
            return
        super()._validate_init_data()

    @cached_property
    def _parent_id(self) -> int:
        parents = ObjectParents(grand_parent_name=None,
                                parent_name=self._category_name)
        return self._parents_to_id_table[parents]


class GroupFactory(BaseFactory):
    """TODO: category and subcategory name to _"""

    _creating_type = ElType.GROUP

    def __init__(self, category_name: str,
                 subcategory_name: str | None = None, **kwargs) -> None:
        self._category_name = category_name
        self._subcategory_name = subcategory_name
        super().__init__()

    def _validate_init_data(self) -> None:
        if self._category_name and self._subcategory_name != '':
            return
        super()._validate_init_data()

    @cached_property
    def _parent_id(self) -> int:
        grandparent = self._category_name if self._subcategory_name else None
        parent = self._subcategory_name if self._subcategory_name\
            else self._category_name
        return self._parents_to_id_table[ObjectParents(grandparent, parent)]
