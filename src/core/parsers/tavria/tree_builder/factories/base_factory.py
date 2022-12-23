"""Base factory class to inheritate from."""
from collections import deque
from collections.abc import Mapping
from typing import ClassVar

from pydantic import BaseModel, Field

from .....core_typing import BaseFactoryReturnType
from .....core_typing import FolderParents


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
