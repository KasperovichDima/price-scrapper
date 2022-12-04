"""
Project Interfaces.
TODO: Move all docstrings here.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, NamedTuple

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
    def get_report(self, header_data: Any,
                   user: IUser, session: Session) -> Any:
        """Start parsing process and get completed report."""


class IRequest(ABC):
    """Request interface."""

    @property
    @abstractmethod
    def element_ids(self) -> cat_elements:
        """Catalog elements of current report."""

    @abstractmethod
    def add_elements(self, elements: cat_elements) -> None:
        """Add catalog elements to current report."""

    @abstractmethod
    def remove_elements(self, elements: cat_elements) -> None:
        """Remove catalog elements from current report."""

    @property
    @abstractmethod
    def retailer_names(self) -> list[str]:
        """Retailers of current report."""

    @abstractmethod
    def add_retailers(self, retailers: Iterable[str]) -> None:
        """Add retailers elements to current report."""

    @abstractmethod
    def remove_retailers(self, retailers: Iterable[str]) -> None:
        """Remove retailers from current report."""

    @abstractmethod
    def get_parser_data(self, header_data: BaseModel,
                        session: Session) -> NamedTuple:
        """Prepare data, required for parsing operation."""


class IElement(BaseWithID):
    """Catalog element interface."""


# class IWebPage(BaseWithID):
#     """WebPage interface."""


class IProduct(BaseWithID):
    """Product intrface."""


class IRetailer(BaseWithID):
    """Retailer interface."""

    name: str


# class IReportHeader(BaseWithID):
#     """ReportHeader interface."""
