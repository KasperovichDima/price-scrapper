"""
Report manager class and instance.
TODO: Connect ParserDataCreator.
"""
from collections import defaultdict
from typing import Any

import interfaces as i

from report.schemas import ReportHeaderBase, ReportHeaderIn

from sqlalchemy.orm import Session

from .request import Request
from ..parsers import Parser
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

    def get_request(self, user: i.IUser) -> i.IRequest:
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

    def get_report(self, header_data: ReportHeaderBase,
                   user: i.IUser, session: Session) -> Any:
        request = self.get_request(user)
        return Parser()(request.get_parser_data(header_data, session))


report_mngr = ReportManager()


######################################
from authentication.models import User  # noqa


class TestReportManager(ReportManager):
    """Test class for report manager."""

    def __init__(self) -> None:
        self.__get_test_request()

    def __get_test_request(self) -> None:
        """Generate fake test request."""

        request = self.get_request(self.__get_fake_user())
        request.add_elements({'Group': [1, 2, 3, 4], 'Product': [1, 2, 3, 4]})
        request.add_retailers('Tavria Silpo Auchan'.split())

    def __get_fake_user(self) -> i.IUser:
        """Returns fake user."""

        return User(
            first_name='Fake',
            last_name='Fake',
            email='fake@fake.com',
            password='fakepasswd',
        )

    def __get_fake_header_data(self) -> ReportHeaderIn:
        """Returns fake header data."""

        return ReportHeaderIn(name='Fake report', note='Fake note')

    def test_get_report(self, session: Session):
        """Main report manager method test. Test all report creating system."""

        header = self.__get_fake_header_data()
        user = self.__get_fake_user()
        report = self.get_report(header, user, session)
