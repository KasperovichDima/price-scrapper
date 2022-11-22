"""Main parser class."""
from typing import Any

import interfaces as i

from sqlalchemy.orm import Session

from report.models import ReportHeader
from report.models import ReportLine

from database.models import WebPage


class Parser(i.IParser):
    """
    Parser class. Strategy pattern used here for different behaviour with
    different retailers. Parser is just callable and need request to process.
    """

    __strategy: i.IParserStrategy

    def __call__(self, request: i.IRequest, session: Session) -> Any:

        products = request.get_products(session)

        retailers = request.get_retailers(session)
        header = ReportHeader(**request.header_data.dict())
        for _ in retailers:
            self.__set_strategy(_)
            links = session.query(WebPage).filter(WebPage.retailer_id == _.id and WebPage.product_id in (product.id for product in products))

    def __set_strategy(self, retailer: i.IRetailer) -> None:
        """Set parsing strategy for specified retailer."""
        ...
