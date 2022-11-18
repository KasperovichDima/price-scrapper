"""Project Interfaces."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

from project_typing import cat_elements


# class IElement(ABC):
#     """Catalog element interface."""


# class IRetailer(ABC):
#     """Shop interface."""


class IUser(ABC):
    """User interface."""


class IReportManager(ABC):
    """ReportManager interface."""

    @abstractmethod
    def get_request(self, user: IUser) -> Any:
        ...

    @abstractmethod
    def add_request_data(self, user: IUser, data: Any) -> Any:
        ...

    @abstractmethod
    def remove_request_data(self, user: IUser, data: Any) -> Any:
        ...

    @abstractmethod
    def get_report(self, user: IUser) -> Any:
        ...


class IRequest(ABC):
    """Request interface."""

    @property
    @abstractmethod
    def elements(self) -> cat_elements:
        ...

    @abstractmethod
    def add_elements(self, elements: cat_elements) -> None:
        ...

    @abstractmethod
    def remove_elements(self, elements: cat_elements) -> None:
        ...

    @property
    @abstractmethod
    def retailers(self) -> list[str]:
        ...

    @abstractmethod
    def add_retailers(self, retailers: Iterable[Any]) -> None:
        ...

    @abstractmethod
    def remove_retailers(self, retailers: Iterable[Any]) -> None:
        ...

    @abstractmethod
    def get_products(self) -> None:
        ...


class IElement(ABC):
    """Catalog element interface."""

    @property
    @abstractmethod
    def content(self) -> Iterable[IElement]:
        ...
