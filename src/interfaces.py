"""Project Interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Iterable


# class IElement(ABC):
#     """Catalog element interface."""


# class IRetailer(ABC):
#     """Shop interface."""


class IUser(ABC):
    """User interface."""


class IReportManager(ABC):
    """ReportManager interface."""

    @abstractmethod
    def get_elements(self, user: IUser) -> dict:
        ...

    @abstractmethod
    def add_elements(self, user: IUser, elements: Iterable[Any]) -> None:
        ...

    @abstractmethod
    def remove_elements(self, user: IUser,
                        elements: Iterable[Any]) -> None:
        ...

    @abstractmethod
    def get_retailers(self, user: IUser) -> list:
        ...

    @abstractmethod
    def add_retailers(self, user: IUser,
                      retailers: Iterable[Any]) -> None:
        ...

    @abstractmethod
    def remove_retailers(self, user: IUser,
                         retailers: Iterable[Any]) -> None:
        ...


class IRequest(ABC):
    """Request interface."""

    @property
    @abstractmethod
    def elements(self) -> dict[str, list[int]]:
        ...

    @abstractmethod
    def add_elements(self, elements: Iterable[Any]) -> None:
        ...

    @abstractmethod
    def remove_elements(self, elements: Iterable[Any]) -> None:
        ...

    @property
    @abstractmethod
    def retailers(self) -> list:
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
