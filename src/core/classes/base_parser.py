"""Base parser class."""
from typing import Iterable

import models as m
import interfaces as i


class BaseParser(i.IParser):
    """Base parser with template method."""
    __id: int   #   how to get self id?
    __report_id: int
    __products: Iterable[m.Product]   #   how to get products from elements?
    __report_lines: Iterable[m.ReportLine]

    def __init__(self, report_id: int, elements: Iterable[i.ICatalogElement]) -> None:
        self.__report_id = report_id

    def perform(self) -> None:
        self.__report_lines = (m.ReportLine(
            self.__report_id,
            product.id,
            self.__id,
            self.__get_reatil_price(product),
            self.__get_promo_price(product)
        ) for product in self.__products)
        crud.bulk_insert(self.__report_lines)
