"""Request class."""
from typing import Any, Iterable

import interfaces as i

from project_typing import cat_elements


class Request(i.IRequest):
    """Request for new report. Contain all required information: products,
    retailers, parameters. Also provides request operations, like get, add,
    remove request data. TODO: datatype for elements."""

    __elements: dict[str, set[int]] = {}
    __retailers: set[str] = set()

    __products: list = []

    @property
    def elements(self) -> cat_elements:
        """Catalog elements of current report."""
        return {cls_name: sorted(list(ids))
                for cls_name, ids in self.__elements.items()}

    def add_elements(self, elements: cat_elements) -> None:
        """Add catalog elements to current report."""

        for cls_name, ids in elements.items():
            try:
                self.__elements[cls_name].update(ids)
            except KeyError:
                self.__elements[cls_name] = set(ids)

    def remove_elements(self, elements: cat_elements) -> None:
        """Remove catalog elements from current report."""

        for cls_name, ids in elements.items():
            try:
                self.__elements[cls_name].difference_update(ids)
            except KeyError:
                continue

    @property
    def retailers(self) -> list:
        """Retailers of current report."""

        return sorted(list(self.__retailers))

    def add_retailers(self, retailers: Iterable[str]) -> None:
        """Add retailers elements to current report."""

        self.__retailers.update(retailers)

    def remove_retailers(self, retailers: Iterable[Any]) -> None:
        """Remove retailers from current report."""

        self.__retailers.difference_update(retailers)

    def get_products(self) -> None:
        ...
