"""Tavria parser typing."""
from typing import NamedTuple
from typing import Generator

from catalog.models import BaseCatalogElement


class ObjectParents(NamedTuple):
    gp_name: str | None = None
    p_name: str | None = None

    def __bool__(self) -> bool:
        return any((self.gp_name, self.p_name))


BaseFactoryReturnType = Generator[BaseCatalogElement, None, None]
