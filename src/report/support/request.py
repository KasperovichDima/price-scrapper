"""Request class."""
from typing import Any, Iterable

import interfaces as i

from project_typing import cat_elements


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

        for cls_name, ids in elements.items():
            if cls_name in self.__elements:
                self.__elements[cls_name].update(ids)
            else:
                self.__elements[cls_name] = set(ids)

    def remove_elements(self, elements: cat_elements) -> None:
        """Remove catalog elements from current report.
        TODO: Add exceptions."""

        for cls_name, ids in elements.items():
            self.__elements[cls_name].difference_update(ids)

    @property
    def retailers(self) -> list:
        ...

    def add_retailers(self, retailers: Iterable[Any]) -> None:
        ...

    def remove_retailers(self, retailers: Iterable[Any]) -> None:
        ...

    def get_products(self) -> None:
        ...
