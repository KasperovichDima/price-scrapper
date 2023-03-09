"""Tavria parser typing."""
from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Iterable, Iterator, NamedTuple, Type

from catalog.models import BaseCatalogElement, Product

from database import int_id

from project_typing import NameRetailPromo, PriceTuple

from .tavria_typing import Path


@dataclass(repr=False, eq=False, kw_only=True, frozen=True, slots=True)
class ToSwitchStatus:
    """Contains information about objects, whose
    'deprecated' status needs to be changed.
    NOTE: All objects must be the same class."""

    cls_: Type[BaseCatalogElement]
    ids_to_depr: Iterable[int]
    ids_to_undepr: Iterable[int]


class FactoryResults(NamedTuple):
    folder_path: Path
    records: deque[NameRetailPromo]

    def get_new_names(self, existing_names: Iterable[str]) -> list[str]:
        return [_[0] for _ in self.records if _[0] not in existing_names]

    def get_page_product_ids(self,
                             name_to_id: Mapping[str, int_id]
                             ) -> set[int]:
        return {name_to_id[_[0]] for _ in self.records if _[0] in name_to_id}

    def get_price_tuples(self,
                         retailer_id: int,
                         name_to_id: Mapping[str, int_id]
                         ) -> Iterator[PriceTuple]:
        return zip((name_to_id[rec[0]] for rec in self.records),
                   (retailer_id for _ in self.records),
                   (rec[1] for rec in self.records),
                   (rec[2] for rec in self.records),
                   strict=True)


@dataclass(eq=False, order=False, slots=True)
class ParsedProducts:
    """
    Container class for:
        1. product names
        2. deprecated product ids
        3. actual product ids
    of all products, saved in database for specified group.
    """
    names: set[str] = field(default_factory=set)
    depr_ids: set[int] = field(default_factory=set)
    actual_ids: set[int] = field(default_factory=set)

    @classmethod
    def from_products(cls, products: Iterable[Product]) -> ParsedProducts:
        """ALternative constructor to get
        DBParsed instance from iterable products."""
        parsed = ParsedProducts()
        if not products:
            return parsed
        for _ in products:
            parsed.names.add(_.name)
            (parsed.depr_ids.add(_.id) if _.deprecated
             else parsed.actual_ids.add(_.id))

        assert parsed.names and (parsed.actual_ids or parsed.depr_ids)
        return parsed

    def get_to_switch(self, page_ids: set[int]) -> ToSwitchStatus | None:
        to_depr = self.actual_ids - page_ids
        to_undepr = self.depr_ids & page_ids
        if any((to_depr, to_undepr)):
            return ToSwitchStatus(
                cls_=Product,
                ids_to_depr=to_depr,
                ids_to_undepr=to_undepr
            )
        return None
