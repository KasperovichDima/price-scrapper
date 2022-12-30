"""Base factory class to inheritate from."""
from collections import deque
from collections.abc import Mapping
from functools import cached_property
from typing import ClassVar

from catalog.models import BaseCatalogElement, Folder

from project_typing import ElType

from pydantic import BaseModel, Field

# from .....core_typing import BaseFactoryReturnType
from ...tavria_typing import BaseFactoryReturnType
from ...tavria_typing import ObjectParents


class BaseFactory(BaseModel):
    """Contains all required information for catalog objects
    cretion. Creates objects using create_objects method."""

    _creating_type: ClassVar[ElType]
    _creating_class: ClassVar[type[BaseCatalogElement]] = Folder
    parents_to_id_table: ClassVar[Mapping[ObjectParents, int]]

    object_names: deque[str] = Field(default_factory=deque)

    def __bool__(self) -> bool:
        return bool(self.object_names)

    def add_name(self, name: str) -> None:
        self.object_names.append(name)

    def get_objects(self) -> BaseFactoryReturnType:
        """Create and return factory objects. Template method."""
        return (self._creating_class(name=name,
                                     parent_id=self._parent_id,
                                     el_type=self._creating_type)
                for name in self.object_names)

    @property
    def _parent_id(self) -> int | None: ...

    class Config:
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)
