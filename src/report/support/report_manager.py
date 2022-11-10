"""Report manager class and instance."""
from typing import Any, Iterable

import interfaces as i

from report.schemas import AddInstanceSchema

from .request import Request


class ReportManager(i.IReportManager):
    """
    Class for handling reports. Can create reports and perform all report
    operations. Primarily - we need to create a user request. Every user has
    he's own request with all request parameters. Any changes will affect only
    current user request. When requst is rady, we can perform parsing and
    report creation process.
    """

    __requests: dict[i.IUser, Request] = {}

    def get_elements(self, user: i.IUser) -> dict[str, list[int]]:
        """Get catalog elements of current user's report."""

        return self.__get_request(user).elements

    def add_elements(self, user: i.IUser,
                     elements: Iterable[AddInstanceSchema]) -> None:
        """Add catalog elements to current user's report."""

        self.__get_request(user).add_elements(elements)

    def __get_request(self, user) -> i.IRequest:
        """Return request of current user, if exists.
        If not - empty request will be created."""

        try:
            self.__requests[user]
        except KeyError:
            self.__requests[user] = Request()
        finally:
            return self.__requests[user]

    def remove_elements(self, user: i.IUser,
                        elements: Iterable[Any]) -> None:
        """Remove catalog elements from current user's report."""

    def get_retailers(self, user: i.IUser) -> list:
        """Get retailers of current user's report."""

    def add_retailers(self, user: i.IUser,
                      retailers: Iterable[Any]) -> None:
        """Add retailers to current user's report."""

    def remove_retailers(self, user: i.IUser,
                         retailers: Iterable[Any]) -> None:
        """Remove retailers from current user's report."""


report_mngr = ReportManager()
