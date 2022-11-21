"""Report manager class and instance."""
from typing import Any

import interfaces as i

from report.models import ReportHeader
from report.schemas import ReportHeaderBase

from sqlalchemy.orm import Session

from .request import Request
from ..exceptions import empty_request_exception
from ..parsers import get_parsers
from ..schemas import RequestDataScheme


class ReportManager(i.IReportManager):
    """
    Class for handling reports. Can create reports and perform all report
    operations. Primarily - we need to create a user request. Every user has
    he's own request with all request parameters. Any changes will affect only
    current user request. When requst is rady, we can perform parsing and
    report creation process.
    """

    __requests: dict[i.IUser, Request] = {}

    def get_request(self, user: i.IUser) -> RequestDataScheme:
        """Get catalog elements and retailers of current user's report."""

        request = self.__get_request(user)
        return RequestDataScheme(
            elements=request.elements,
            retailers=request.retailers
        )

    def __get_request(self, user: i.IUser) -> i.IRequest:
        """Return request of current user, if exists.
        If not - empty request will be created."""

        try:
            self.__requests[user]
        except KeyError:
            self.__requests[user] = Request()
        finally:
            return self.__requests[user]

    def add_request_data(self, user: i.IUser,
                         data: RequestDataScheme) -> RequestDataScheme:
        """Add data to current user's report."""

        request = self.__get_request(user)
        if data.elements:
            request.add_elements(data.elements)
        if data.retailers:
            request.add_retailers(data.retailers)
        return RequestDataScheme(
            elements=request.elements,
            retailers=request.retailers
        )

    def remove_request_data(self, user: i.IUser,
                            data: RequestDataScheme) -> RequestDataScheme:
        """Remove data from current user's report."""

        request = self.__get_request(user)
        if data.elements:
            request.remove_elements(data.elements)
        if data.retailers:
            request.remove_retailers(data.retailers)
        return RequestDataScheme(
            elements=request.elements,
            retailers=request.retailers
        )

    def get_report(self, header_payload: ReportHeaderBase,
                   user: i.IUser, session: Session) -> Any:
        """Start parsing process and get completed report."""

        request = self.__get_request(user)
        if not request:
            raise empty_request_exception
        header = ReportHeader(**header_payload.dict())
        products = request.products
        parsers = get_parsers(request.retailers)
        for parser in parsers:
            parser(products)


report_mngr = ReportManager()
