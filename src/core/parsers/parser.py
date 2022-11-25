"""Main parser class."""
from typing import Any

import interfaces as i

from .strategies import BaseStrategy
from ..schemas import ParserData


class Parser:
    """
    Parser class. Strategy pattern used here for different behaviour with
    different retailers. Parser is just callable and need request to process.
    """

    __strategy: BaseStrategy
    __report_data: dict[i.IRetailer, Any] = {}

    def __call__(self, parser_data: ParserData) -> str:
        """
        Parser's main method. Starts parsing process.
        Accepts request instance and returns report.
        """

        for retailer in parser_data.retailers:

            self.__set_strategy(retailer)
            self.__report_data[retailer] = self.__strategy(parser_data)

        return self.__report_data

    def __set_strategy(self, retailer: i.IRetailer) -> None:
        """Set parsing strategy for specified retailer."""
        ...
