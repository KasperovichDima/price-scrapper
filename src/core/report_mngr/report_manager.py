"""Report manager class and instance."""
from collections import defaultdict
from typing import Any

import interfaces as i

from report.schemas import ReportHeaderBase
from report.schemas import ReportHeaderIn

from sqlalchemy.orm import Session

from .request import Request
from ..exceptions import empty_request_exception
from ..parsers import Parser
from ..schemas import RequestDataScheme


class ReportManager(i.IReportManager):
    """
    Class for handling reports. Can create reports and perform all report
    operations. Primarily - we need to create a user request. Every user has
    he's own request with all request parameters. Any changes will affect only
    current user request. When requst is rady, we can perform parsing and
    report creation process.
    """

    __requests: defaultdict[i.IUser, Request] = defaultdict(Request)

    def get_request(self, user: i.IUser) -> i.IRequest:
        """Return request of current user, if exists.
        If not - empty request will be created."""

        return self.__requests[user]

    def add_request_data(self, user: i.IUser,
                         data: RequestDataScheme) -> RequestDataScheme:
        """Add data to current user's report."""

        request = self.get_request(user)
        if data.el_names:
            request.add_elements(data.el_names)
        if data.shop_names:
            request.add_retailers(data.shop_names)
        return RequestDataScheme(
            el_names=request.el_names,
            shop_names=request.shop_names
        )

    def remove_request_data(self, user: i.IUser,
                            data: RequestDataScheme) -> RequestDataScheme:
        """Remove data from current user's report."""

        request = self.get_request(user)
        if data.el_names:
            request.remove_elements(data.el_names)
        if data.shop_names:
            request.remove_retailers(data.shop_names)
        return RequestDataScheme(
            el_names=request.el_names,
            shop_names=request.shop_names
        )

    def get_report(self, header_data: ReportHeaderIn,
                   user: i.IUser, session: Session) -> Any:
        """
        Start parsing process and get completed report.
        TODO: Refactor this method.
        """

        request = self.get_request(user)
        request.header_data = ReportHeaderBase(
            **header_data.dict(),
            user_id=user.id
        )
        if not request:
            raise empty_request_exception
        parser = Parser()

        return parser(request, session)


report_mngr = ReportManager()
