"""Tavria parser typing."""
from collections import deque
from dataclasses import dataclass
from typing import Iterable, NamedTuple, Type

from catalog.models import BaseCatalogElement

from .tavria_typing import Path, NameRetailPromo


@dataclass(repr=False, eq=False, kw_only=True, frozen=True, slots=True)
class ToSwitchStatus:
    """Contains information about objects, whose
    'deprecated' status needs to be changed.
    NOTE: All objects must have same class."""

    cls_: Type[BaseCatalogElement]
    ids_to_depr: Iterable[int]
    ids_to_undepr: Iterable[int]


class FactoryResults(NamedTuple):
    folder_path: Path
    records: deque[NameRetailPromo]
