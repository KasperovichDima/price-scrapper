"""Request class."""
from typing import Iterable

import crud

import interfaces as i

from project_typing import cat_elements

from report.schemas import ReportHeaderBase

from sqlalchemy.orm import Session


class Request(i.IRequest):
    """Request for new report. Contain all required information: products,
    retailers, parameters. Also provides request operations, like get, add,
    remove request data. TODO: datatype for elements."""

    __el_names: dict[str, set[int]] = {}
    __shop_names: set[str] = set()
    __header_data: ReportHeaderBase

    def __bool__(self):
        return bool(self.__el_names
                    and self.shop_names
                    and self.__header_data)
    
    @property
    def header_data(self) -> ReportHeaderBase:
        return self.__header_data
    
    @header_data.setter
    def header_data(self, data: ReportHeaderBase) -> None:
        self.__header_data = data

    @property
    def el_names(self) -> cat_elements:
        """Catalog elements of current report."""
        return {cls_name: sorted(list(ids))
                for cls_name, ids in self.__el_names.items()}

    def add_elements(self, elements: cat_elements) -> None:
        """Add catalog elements to current report."""

        for cls_name, ids in elements.items():
            try:
                self.__el_names[cls_name].update(ids)
            except KeyError:
                self.__el_names[cls_name] = set(ids)

    def remove_elements(self, elements: cat_elements) -> None:
        """Remove catalog elements from current report."""

        for cls_name, ids in elements.items():
            try:
                self.__el_names[cls_name].difference_update(ids)
            except KeyError:
                continue

    @property
    def shop_names(self) -> list[str]:
        """Retailers of current report."""

        return sorted(list(self.__shop_names))

    def add_retailers(self, retailers: Iterable[str]) -> None:
        """Add retailers elements to current report."""

        self.__shop_names.update(retailers)

    def remove_retailers(self, retailers: Iterable[str]) -> None:
        """Remove retailers from current report."""

        self.__shop_names.difference_update(retailers)

    def get_products(self, session: Session) -> Iterable[i.IProduct]:
        """Returns products from all elements."""

    def get_retailers(self, session: Session) -> Iterable[i.IRetailer]:
        """Returns retailer objects of request."""

        return crud.get_retailers(self.__shop_names, session)
