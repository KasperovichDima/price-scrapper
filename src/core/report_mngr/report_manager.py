"""
Report manager class and instance.
TODO: Connect ParserDataCreator.
"""
from collections import defaultdict

import interfaces as i

from sqlalchemy.orm import Session

from .request import Request
from ..core_typing import RequestObjects
from ..schemas import RequestInScheme
from ..utils import get_request_objects


class ReportManager:
    """
    Class for handling reports. Can create reports and perform all report
    operations. Primarily - User request must be created. Every user has
    he's own request with all request parameters. Any changes will affect only
    current user request.
    """

    __requests: defaultdict[i.IUser, Request] = defaultdict(Request)

    def get_request(self, user: i.IUser) -> Request:
        return self.__requests[user]

    def add_request_data(self, user: i.IUser,
                         in_data: RequestInScheme,
                         session: Session) -> RequestObjects:

        request = self.get_request(user)
        request.add_objects(get_request_objects(in_data, session))
        return request.out_data

    def remove_request_data(self, user: i.IUser,
                            in_data: RequestInScheme,
                            session: Session) -> RequestObjects:

        request = self.get_request(user)
        request.remove_objects(get_request_objects(in_data, session))
        return request.out_data

    # def get_report(self, user: i.IUser, session: Session) -> Any:
    #     """TODO: Refactoring."""

    #     request = self.get_request(user)


report_mngr = ReportManager()
