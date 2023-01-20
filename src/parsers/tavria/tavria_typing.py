"""Tavria parser typing."""
from typing import NamedTuple
from typing import Generator

from catalog.models import BaseCatalogElement


# ObjectParents = namedtuple('ObjectParents', 'grand_parent_name parent_name')
class ObjectParents(NamedTuple):
    grand_parent_name: str | None = None
    parent_name: str | None = None

    def __bool__(self) -> bool:
        return any((self.grand_parent_name, self.parent_name))


BaseFactoryReturnType = Generator[BaseCatalogElement, None, None]
