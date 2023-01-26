import reprlib
from functools import cached_property

from catalog.utils import get_class_by_type

from project_typing import ElType

from .objects_box import ObjectsBox
from .parent_table import ParentTable
from .tavria_typing import ObjectParents


class BaseFactory:
    """TODO: Correct params order."""

    _object_box: ObjectsBox

    def __init__(self,
                 el_type: ElType,
                 *args,
                 category_name: str | None = None,
                 subcategory_name: str | None = None,
                 group_name: str | None = None,
                 **kwds) -> None:
        self._el_type = el_type
        self._category_name = category_name
        self._subcategory_name = subcategory_name
        self._group_name = group_name
        self._object_names: list[str] = []

    async def __call__(self, *args, **kwds) -> None:
        """TODO: Devide on 'pre', 'main_process', 'post'."""
        await self._get_new_objects()

    async def _get_new_objects(self):
        cls_ = get_class_by_type(self._el_type)
        new_objects = (cls_(name=name,
                            parent_id=self._parent_id,
                            el_type=self._el_type)
                       for name in self._object_names)
        await self._object_box.add(new_objects)

    @cached_property
    def _parent_id(self) -> int | None:
        if not self._parents:
            return None
        return ParentTable.get_table()[self._parents]

    @cached_property
    def _parents(self) -> ObjectParents:
        """TODO: rename grand_parent_name to gp_name, parent_name to p_name"""
        if self._group_name:
            gp_name = self._subcategory_name if self._subcategory_name\
                else self._category_name
            return ObjectParents(gp_name=gp_name, p_name=self._group_name)
        else:
            p_name = self._subcategory_name if self._subcategory_name\
                else self._category_name
            gp_name = self._category_name if self._subcategory_name else None
            return ObjectParents(gp_name=gp_name, p_name=p_name)

    def __repr__(self) -> str:
        return (f'{self._el_type.name}: '
                f'{reprlib.repr(self._object_names)}')

    def __bool__(self) -> bool:
        return bool(self._object_names)
