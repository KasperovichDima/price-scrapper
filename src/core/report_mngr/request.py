"""Request class."""
from collections import defaultdict
from typing import Iterable

import interfaces as i

from project_typing import cat_elements


class Request(i.IRequest):
    """Request for new report. Contain all required information: products,
    retailers, parameters. Also provides request operations, like get, add,
    remove request data. TODO: datatype for elements."""

    __el_ids: defaultdict[str, set[int]] = defaultdict(set)
    __ret_names: set[str] = set()

    def __bool__(self):
        return bool(self.__el_ids
                    and self.retailer_names)

    @property
    def element_ids(self) -> cat_elements:
        return {cls_name: sorted(ids)
                for cls_name, ids in self.__el_ids.items()}

    def add_elements(self, el_ids: cat_elements) -> None:
        for cls_name, ids in el_ids.items():
            self.__el_ids[cls_name].update(ids)

    def remove_elements(self, el_ids: cat_elements) -> None:
        for cls_name, ids in el_ids.items():
            if cls_name in self.__el_ids:
                self.__el_ids[cls_name].difference_update(ids)

    @property
    def retailer_names(self) -> list[str]:
        return sorted(self.__ret_names)

    def add_retailers(self, ret_ids: Iterable[str]) -> None:
        self.__ret_names.update(ret_ids)

    def remove_retailers(self, ret_ids: Iterable[str]) -> None:
        self.__ret_names.difference_update(ret_ids)
