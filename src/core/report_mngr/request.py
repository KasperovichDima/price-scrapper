"""Request class."""
from collections import defaultdict
from typing import Iterable

import crud

import interfaces as i

from project_typing import cat_elements

from report.schemas import ReportHeaderBase

from sqlalchemy.orm import Session

from ..schemas import RequestDataScheme


class Request(i.IRequest):
    """Request for new report. Contain all required information: products,
    retailers, parameters. Also provides request operations, like get, add,
    remove request data. TODO: datatype for elements."""

    __el_names: defaultdict[str, set[int]] = defaultdict(set)
    __shop_names: set[str] = set()
    __header_data: ReportHeaderBase

    def __bool__(self):
        return bool(self.__el_names
                    and self.shop_names
                    and self.__header_data)

    @property
    def header_data(self) -> ReportHeaderBase | None:
        try:
            return self.__header_data
        except KeyError:
            return

    @header_data.setter
    def header_data(self, data: ReportHeaderBase) -> None:
        self.__header_data = data

    @property
    def el_names(self) -> cat_elements:
        return {cls_name: sorted(ids)
                for cls_name, ids in self.__el_names.items()}

    def add_elements(self, elements: cat_elements) -> None:
        for cls_name, ids in elements.items():
            self.__el_names[cls_name].update(ids)

    def remove_elements(self, elements: cat_elements) -> None:
        for cls_name, ids in elements.items():
            if cls_name in self.__el_names:
                self.__el_names[cls_name].difference_update(ids)

    @property
    def shop_names(self) -> list[str]:
        return sorted(self.__shop_names)

    def add_retailers(self, retailers: Iterable[str]) -> None:
        self.__shop_names.update(retailers)

    def remove_retailers(self, retailers: Iterable[str]) -> None:
        self.__shop_names.difference_update(retailers)

    def get_products(self, session: Session) -> Iterable[i.IProduct]:
        ...

    def get_retailers(self, session: Session) -> Iterable[i.IRetailer]:
        return crud.get_retailers(self.__shop_names, session)

    @property
    def schema(self) -> RequestDataScheme:
        return RequestDataScheme(el_names=self.el_names,
                                 shop_names=self.shop_names)
