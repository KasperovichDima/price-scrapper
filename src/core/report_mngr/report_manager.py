"""Report manager class and instance."""
from typing import Any

import interfaces as i

from report.schemas import ReportHeaderBase
from report.models import ReportHeader

from .request import Request
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

    __requests: dict[int, Request] = {}

    def get_request(self, user: i.IUser) -> RequestDataScheme:
        """Get catalog elements and retailers of current user's report."""

        request = self.__get_request(user.id)
        return RequestDataScheme(
            elements=request.elements,
            retailers=request.retailers
        )

    def __get_request(self, user_id: int) -> i.IRequest:
        """Return request of current user, if exists.
        If not - empty request will be created."""

        try:
            self.__requests[user_id]
        except KeyError:
            self.__requests[user_id] = Request()
        finally:
            return self.__requests[user_id]

    def add_request_data(self, user: i.IUser,
                         data: RequestDataScheme) -> RequestDataScheme:
        """Add data to current user's report."""

        request = self.__get_request(user.id)
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

        request = self.__get_request(user.id)
        if data.elements:
            request.remove_elements(data.elements)
        if data.retailers:
            request.remove_retailers(data.retailers)
        return RequestDataScheme(
            elements=request.elements,
            retailers=request.retailers
        )

    def get_report(self, header_payload: ReportHeaderBase) -> Any:
        """Start parsing process and get completed report."""

        header = ReportHeader(**header_payload.dict())
        request = self.__get_request(header.user_id)  # type: ignore
        products = request.get_products() #  get products for parsing
        parsers = get_parsers(request.retailers) #  get parsers by retailer names
        for parser in parsers: #  start parsing(creating report lines)
            parser(products)


report_mngr = ReportManager()
