"""Request class."""
from collections import defaultdict, deque
from typing import Iterable

import crud

from database.models import WebPage

import interfaces as i

from project_typing import cat_elements

from report.models import ReportHeader
from report.schemas import ReportHeaderBase

from sqlalchemy.orm import Session

from ..core_typing import ParserData, ProductsByURL


class Request(i.IRequest):
    """Request for new report. Contain all required information: products,
    retailers, parameters. Also provides request operations, like get, add,
    remove request data. TODO: datatype for elements."""

    __el_ids: defaultdict[str, set[int]] = defaultdict(set)
    __ret_names: set[str] = set()

    __header: ReportHeader
    __session: Session
    __retailers: list[i.IRetailer]

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

    def get_parser_data(self, header_data: ReportHeaderBase,  # type: ignore
                        session: Session) -> ParserData:

        self.__session = session
        self.__retailers = crud.get_retailers(self.__ret_names, session)

        self.__create_header(header_data)

        return ParserData(
            header_id=self.__header.id,  # type: ignore
            products_by_url=self.__get_products_by_url(session),
            retailers=self.__retailers,
            session=session
        )

    def __create_header(self, header_data: ReportHeaderBase) -> None:
        self.__header = ReportHeader(**header_data.dict())
        crud.add_instance(self.__header, self.__session)

    def __get_products_by_url(self, session: Session) -> ProductsByURL:
        """Returns products, sorted by urls."""

        products_by_url: ProductsByURL = defaultdict(deque)
        for page in self.__get_pages(session):
            products_by_url[page.url].append(page.product)  # type: ignore

        return products_by_url

    def __get_pages(self, session: Session) -> list[WebPage]:
        """
        Get web pages(links), containing request products.
        TODO: It seems, we need dict here. Retailer: Pages.
        """

        pages = []
        product_ids = {_.id for _ in self.__get_products(session)}
        for rtl in self.__retailers:
            query = session.query(WebPage)
            query = query.filter_by(retailer_id=rtl.id)
            query = query.filter(WebPage.product_id.in_(product_ids))
            pages.extend(query.all())

        return pages

    def __get_products(self, session: Session) -> Iterable[i.IProduct]:
        return crud.get_products(self.__el_ids, session)
