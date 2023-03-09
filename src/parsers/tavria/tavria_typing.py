"""Tavria parser typing."""
from collections import deque
from dataclasses import dataclass
from typing import Iterable, NamedTuple, Protocol, Type

from catalog.models import BaseCatalogElement

from project_typing import NameRetailPromo


Path = tuple[str, str | None, str | None]


class Catalog_P(Protocol):
    """Implementation of product catalog tree. Main functions are:
        1. update - synchronize catalog structure in database with web page.
        2. get_id_by_path - will return you id of folder, specified by path."""

    async def update(self) -> None:
        """Get actual data from the page
        and update in_db catalog structure."""

    def get_id_by_path(self, path: Path) -> int:
        """Get id of folder with specified path."""


@dataclass(repr=False, eq=False, kw_only=True, frozen=True, slots=True)
class ToSwitchStatus:
    """Contains information about objects, whose
    'deprecated' status needs to be changed.
    NOTE: All objects must have same class."""

    cls_: Type[BaseCatalogElement]
    ids_to_depr: Iterable[int]
    ids_to_undepr: Iterable[int]


class Results(NamedTuple):
    folder_path: Path
    records: deque[NameRetailPromo]
