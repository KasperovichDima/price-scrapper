"""Project interfaces."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Optional


class IUser(ABC):
    """User interface."""
    id: int


class ICatalogElement(ABC):
    """Catalog Element interface."""

    id: int
    content: Iterable[ICatalogElement]
    content_class: Optional[str]

    def get_products(self) -> Iterable[ICatalogElement]:
        """Get all products of current element."""


class IShop(ABC):
    """Shop interface."""


class IRequest(ABC):
    """Request interface."""

    name: str
    user: IUser

    @abstractmethod
    def add_elements(self, elements: Iterable[ICatalogElement]) -> None:
        """Add catalog elements to user request."""

    @abstractmethod
    def remove_elements(self, elements: Iterable[ICatalogElement]) -> None:
        """Remove catalog elements from user request."""

    @abstractmethod
    def add_shops(self, shops: Iterable[IShop]) -> None:
        """Add shops to user request."""

    @abstractmethod
    def remove_shops(self, shops: Iterable[IShop]) -> None:
        """Remove shops from user request."""

    @property
    @abstractmethod
    def products(self) -> Iterable[ICatalogElement]:
        """Get request products."""

    @property
    @abstractmethod
    def shops(self) -> Iterable[IShop]:
        """Get request shops."""


class IReport(ABC):
    """Report interface."""


class IReportString(ABC):
    """ReportString interface."""


class IParser(ABC):
    """Parser interface. Template method realization."""

    @abstractmethod
    def add_prices(self, report: IReport) -> None:
        """
        set self.__shop
        sort by this shop groups
        get prices group by group
        set new product prices
        save report to database
        """
