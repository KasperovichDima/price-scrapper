"""Main parser class."""
from collections import deque
from typing import Any, Set

import interfaces as i

from sqlalchemy.orm import Session

from report.models import ReportHeader
from report.models import ReportLine

from database.models import WebPage


class Parser(i.IParser):
    """
    Parser class. Strategy pattern used here for different behaviour with
    different retailers. Parser is just callable and need request to process.
    TODO: Refactoring __call__ and flake check needed.
    """

    __strategy: i.IParserStrategy
    __report_data: dict[i.IRetailer, Any] = {}

    def __call__(self, request: i.IRequest, session: Session) -> Any:

        products = request.get_products(session)
        retailers = request.get_retailers(session)
        header = ReportHeader(**request.header_data.dict())
        for _ in retailers:
            product_pages: list[WebPage] = session.query(WebPage).filter_by(retailer_id=_.id).filter(WebPage.product_id.in_(_.id for _ in products)).all()
            # prod_by_url = {page.url: page.product_id for page in product_pages}
            prod_by_url: dict[str, deque[i.IProduct]] = {}  # adopt cat_elements here and rename it
            for _ in product_pages:
                try:
                    prod_by_url[_.url]
                except KeyError:
                    prod_by_url[_.url] = deque()
                finally:
                    prod_by_url[_.url].append(_.product)
            self.__set_strategy(_)
            data_for_parser = dict(header_id=header.id, retailer_id=_.id, prod_by_url=prod_by_url)
            self.__report_data[_] = self.__strategy(data_for_parser)

        return self.__report_data






    def __set_strategy(self, retailer: i.IRetailer) -> None:
        """Set parsing strategy for specified retailer."""
        ...
