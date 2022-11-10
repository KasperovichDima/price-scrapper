"""Request class."""
from typing import Any, Iterable

import interfaces as i

from ..schemas import AddInstanceSchema


class Request(i.IRequest):
    """Request for new report. Contain all required information: products,
    retailers, parameters. Also provides request operations, like get, add,
    remove request data. TODO: datatype for elements."""

    __elements: dict[str, set[int]] = {}
    __products: list = []

    __retailers: list = []

    @property
    def elements(self) -> dict[str, list[int]]:
        """Catalog elements of current report."""
        return {cls_name: sorted(list(ids))
                for cls_name, ids in self.__elements.items()}

    def add_elements(self, elements: Iterable[AddInstanceSchema]) -> None:
        """Add catalog elements to current report."""

        for el in elements:
            if el.class_name in self.__elements:
                self.__elements[el.class_name].update(el.ids)
            else:
                self.__elements[el.class_name] = set(el.ids)

    def remove_elements(self, elements: Iterable[Any]) -> None:
        ...

    @property
    def retailers(self) -> list:
        ...

    def add_retailers(self, retailers: Iterable[Any]) -> None:
        ...

    def remove_retailers(self, retailers: Iterable[Any]) -> None:
        ...

    def get_products(self) -> None:
        ...
