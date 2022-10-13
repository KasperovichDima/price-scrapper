"""Module for creating and processing new reports."""
from typing import Iterable, List
import models as m
import interfaces as i


class ReportManager:
    """Creates and perform all operations with reports."""
    __report_id: int

    __shops: List[i.IShop] = []
    __elements: List[i.ICatalogElement] = []

    def create_report(self, name: str, note: str, user: i.IUser) -> None:
        """Create new report."""
        report = m.Report(name, note, user.id)
        self.__report_id = report.id

    def add_elements(self, elements: Iterable[i.ICatalogElement]) -> None:
        """Add catalog elements to user request."""
        self.__elements.extend(elements)

    def remove_elements(self, elements: Iterable[i.ICatalogElement]) -> None:
        """Remove catalog elements from user request.
        TODO: need to be optimized."""
        for _ in elements:
            if _ in self.__elements:
                self.__elements.remove(_)

    def add_shops(self, shops: Iterable[i.IShop]) -> None:
        """Add shops to user request."""
        self.__shops.extend(shops)

    def remove_shops(self, shops: Iterable[i.IShop]) -> None:
        """Remove shops from user request.
        TODO: need to be optimized."""
        for _ in shops:
            if _ in self.__shops:
                self.__shops.remove(_)

    def fill_report(self) -> None:
        """Create report, fill it with products, shops and prices. Then save to database."""
        if not self.__elements:
            return


report_manager = ReportManager()
