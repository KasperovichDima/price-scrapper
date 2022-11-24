"""
Project Interfaces.
TODO: Move all docstrings here.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

from project_typing import cat_elements

from sqlalchemy.orm import Session

from pydantic import BaseModel


class BaseWithID(ABC):
    """Base interface, containing id: int."""

    id: int


class IUser(BaseWithID):
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
    def get_report(self, header_payload: Any,
                   user: IUser, session: Session) -> Any:
        ...


class IRequest(ABC):
    """Request interface."""

    @property
    @abstractmethod
    def header_data(self) -> BaseModel:
        ...
    
    @header_data.setter
    @abstractmethod
    def header_data(self, data: BaseModel) -> None:
        ...

    @property
    @abstractmethod
    def el_names(self) -> cat_elements:
        ...

    @abstractmethod
    def add_elements(self, elements: cat_elements) -> None:
        ...

    @abstractmethod
    def remove_elements(self, elements: cat_elements) -> None:
        ...

    @property
    @abstractmethod
    def shop_names(self) -> list[str]:
        ...

    @abstractmethod
    def add_retailers(self, retailers: Iterable[str]) -> None:
        ...

    @abstractmethod
    def remove_retailers(self, retailers: Iterable[str]) -> None:
        ...

    @abstractmethod
    def get_products(self, session: Session) -> Iterable[IProduct]:
        ...

    @abstractmethod
    def get_retailers(self, session: Session) -> Iterable[IRetailer]:
        ...


class IElement(BaseWithID):
    """Catalog element interface."""

    @property
    @abstractmethod
    def content(self) -> Iterable[IElement]:
        ...


class IWebPage(BaseWithID):
    """WebPage interface."""


class IProduct(BaseWithID):
    """Product intrface."""

    # @abstractmethod
    # def get_page_by_retailer(self, retailer: IRetailer) -> str:
    #     """Get web page, containing this product in specified retailers shop."""


class IParser(ABC):
    """Parser interface."""

    def __call__(self, request: IRequest, session: Session) -> Any:
        ...


class IRetailer(BaseWithID):
    """Retailer interface."""


# class IParserStrategy(ABC):
#     """Parser strategy interface."""

#     def __call__(self, pars_data: BaseModel) -> Any:
#         ...
