"""Request class."""
from typing import Any, Iterable

import interfaces as i

from ..schemas import cat_elements


class Request(i.IRequest):
    """Request for new report. Contain all required information: products,
    retailers, parameters. Also provides request operations, like get, add,
    remove request data. TODO: datatype for elements."""

    __elements: dict[str, set[int]] = {}
    __products: list = []

    __retailers: list = []

    @property
    def elements(self) -> cat_elements:
        """Catalog elements of current report."""
        return {cls_name: sorted(list(ids))
                for cls_name, ids in self.__elements.items()}

    def add_elements(self, elements: cat_elements) -> None:
        """Add catalog elements to current report."""

        for k, v in elements.items():
            if k in self.__elements:
                self.__elements[k].update(v)
            else:
                self.__elements[k] = set(v)

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
