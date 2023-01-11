"""
Base factory class to inheritate from.
TODO: use slots.
"""
from collections.abc import Mapping
from functools import cached_property

from catalog.models import BaseCatalogElement, Folder

from project_typing import ElType

from .exceptions import EmptyFactoryDataError
from ...tavria_typing import BaseFactoryReturnType
from ...tavria_typing import ObjectParents


class BaseFactory:
    """Contains all required information for catalog objects
    cretion. Creates objects using create_objects method."""

    _creating_type: ElType
    _creating_class: type[BaseCatalogElement] = Folder
    _parents_to_id_table: Mapping[ObjectParents, int]

    def __init__(self, **kwargs) -> None:
        self._validate_init_data()
        self._object_names: set[str] = set()

    def add_name(self, name: str) -> None:
        self._object_names.add(name)

    def get_objects(self) -> BaseFactoryReturnType:
        """Create and return factory objects. Template method."""

        return (self._creating_class(name=name,
                                     parent_id=self._parent_id,
                                     el_type=self._creating_type)
                for name in self._object_names)

    @classmethod
    def refresh_parent_table(cls, table: Mapping[ObjectParents, int]) -> None:
        """Set new parent to id table as a class variable."""

        cls._parents_to_id_table = table

    def _validate_init_data(self) -> None:
        """Validates init data. Raises EmptyFactoryDataError
        if required data miss or is empty."""
        raise EmptyFactoryDataError('Some of init data args are empty.')

    @cached_property
    def _parent_id(self) -> int | None: ...

    def __bool__(self) -> bool:
        return bool(self._object_names)
