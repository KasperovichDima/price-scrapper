"""Project Interfaces."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

from project_typing import cat_elements

from sqlalchemy.orm import Session


class IUser(ABC):
    """User interface."""

    id: int


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
    def get_report(self, header_payload: Any, user: IUser, session: Session) -> Any:
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
    def add_retailers(self, retailers: Iterable[str]) -> None:
        ...

    @abstractmethod
    def remove_retailers(self, retailers: Iterable[str]) -> None:
        ...

    @property
    @abstractmethod
    def products(self) -> Iterable[IProduct]:
        ...


class IElement(ABC):
    """Catalog element interface."""

    @property
    @abstractmethod
    def content(self) -> Iterable[IElement]:
        ...


class IProduct(ABC):
    """Product intrface."""


class IParser(ABC):
    """Parser interface."""

    def __call__(self, products: Iterable[IProduct]) -> Any:
        ...
    
