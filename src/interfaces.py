"""Project Interfaces."""
from abc import ABC, abstractmethod
from typing import Iterable

from project_typing import UserType


class IUser(ABC):
    """User interface."""

    id: int
    first_name: str
    last_name: str
    email: str
    password: str
    is_active: bool
    type: UserType


class IReportManager(ABC):
    """ReportManager interface."""

    @abstractmethod
    def add_products(self, user: IUser, products: Iterable):
        """Add product instances to request of current user."""

    @abstractmethod
    def get_products(self, user: IUser) -> list:
        """Returns product instances from current user's report."""
