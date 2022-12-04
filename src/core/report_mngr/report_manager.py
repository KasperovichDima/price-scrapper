"""
Report manager class and instance.
TODO: Connect ParserDataCreator.
"""
from collections import defaultdict
from typing import Any

import interfaces as i

from sqlalchemy.orm import Session

from .request import Request
from ..schemas import RequestDataScheme


class ReportManager(i.IReportManager):
    """
    Class for handling reports. Can create reports and perform all report
    operations. Primarily - User request must be created. Every user has
    he's own request with all request parameters. Any changes will affect only
    current user request. When request is ready, parsing and report creation
    process can be performed.
    """

    __requests: defaultdict[i.IUser, Request] = defaultdict(Request)

    def get_request(self, user: i.IUser) -> Request:
        return self.__requests[user]

    def add_request_data(self, user: i.IUser,
                         data: RequestDataScheme) -> RequestDataScheme:
        request = self.get_request(user)

        if data.el_ids:
            request.add_elements(data.el_ids)
        if data.ret_names:
            request.add_retailers(data.ret_names)
        return RequestDataScheme(
            el_ids=request.element_ids,
            ret_names=request.retailer_names
        )

    def remove_request_data(self, user: i.IUser,
                            data: RequestDataScheme) -> RequestDataScheme:
        request = self.get_request(user)
        if data.el_ids:
            request.remove_elements(data.el_ids)
        if data.ret_names:
            request.remove_retailers(data.ret_names)
        return RequestDataScheme(
            el_ids=request.element_ids,
            ret_names=request.retailer_names
        )

    def get_report(self, user: i.IUser, session: Session) -> Any:
        """TODO: Refactoring."""

        request = self.get_request(user)


report_mngr = ReportManager()
