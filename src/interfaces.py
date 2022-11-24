"""
Project Interfaces.
TODO: Move all docstrings here.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

from project_typing import cat_elements

from pydantic import BaseModel

from sqlalchemy.orm import Session


class BaseWithID(ABC):
    """Base interface, containing id: int."""

    id: int


class IUser(BaseWithID):
    """User interface."""


class IReportManager(ABC):
    """ReportManager interface."""

    @abstractmethod
    def get_request(self, user: IUser) -> IRequest:
        """Return request of current user, if exists.
        If not - empty request will be created."""

    @abstractmethod
    def add_request_data(self, user: IUser, data: Any) -> Any:
        """Add data to current user's report."""

    @abstractmethod
    def remove_request_data(self, user: IUser, data: Any) -> Any:
        """Remove data from current user's report."""

    @abstractmethod
    def get_report(self, header_payload: Any,
                   user: IUser, session: Session) -> Any:
        """Start parsing process and get completed report."""


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
        """Catalog elements of current report."""

    @abstractmethod
    def add_elements(self, elements: cat_elements) -> None:
        """Add catalog elements to current report."""

    @abstractmethod
    def remove_elements(self, elements: cat_elements) -> None:
        """Remove catalog elements from current report."""

    @property
    @abstractmethod
    def shop_names(self) -> list[str]:
        """Retailers of current report."""

    @abstractmethod
    def add_retailers(self, retailers: Iterable[str]) -> None:
        """Add retailers elements to current report."""

    @abstractmethod
    def remove_retailers(self, retailers: Iterable[str]) -> None:
        """Remove retailers from current report."""

    @abstractmethod
    def get_products(self, session: Session) -> Iterable[IProduct]:
        """Returns products from all elements."""

    @abstractmethod
    def get_retailers(self, session: Session) -> Iterable[IRetailer]:
        """Returns retailer objects of request."""

    @property
    @abstractmethod
    def schema(self) -> BaseModel:
        """Get validated pydantic representation of the request."""


class IElement(BaseWithID):
    """Catalog element interface."""

    @property
    @abstractmethod
    def content(self) -> Iterable[IElement]:
        """Content of current catalog instance."""


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
        """
        Parser's main method. Starts parsing process.
        Accepts request instance and returns report.
        """


class IRetailer(BaseWithID):
    """Retailer interface."""


# class IParserStrategy(ABC):
#     """Parser strategy interface."""

#     def __call__(self, pars_data: BaseModel) -> Any:
#         ...
