"""Report manager class and instance."""
from collections import defaultdict, deque
from typing import Any

import crud

from database.models import WebPage

import interfaces as i

from pydantic import BaseModel

from report.models import ReportHeader
from report.schemas import ReportHeaderBase

from sqlalchemy.orm import Session

from .request import Request
from ..core_typing import ProductsByURL
from ..parsers import Parser
from ..schemas import ParserData
from ..schemas import RequestDataScheme


class ReportManager(i.IReportManager):
    """
    Class for handling reports. Can create reports and perform all report
    operations. Primarily - we need to create a user request. Every user has
    he's own request with all request parameters. Any changes will affect only
    current user request. When request is ready, we can perform parsing and
    report creation process.
    """

    __requests: defaultdict[i.IUser, Request] = defaultdict(Request)

    def get_request(self, user: i.IUser) -> i.IRequest:
        return self.__requests[user]

    def add_request_data(self, user: i.IUser,
                         data: RequestDataScheme) -> RequestDataScheme:
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
        request = self.get_request(user)
        if data.el_names:
            request.remove_elements(data.el_names)
        if data.shop_names:
            request.remove_retailers(data.shop_names)
        return RequestDataScheme(
            el_names=request.el_names,
            shop_names=request.shop_names
        )

    def get_report(self, header_data: BaseModel,
                   user: i.IUser, session: Session) -> Any:
        request = self.get_request(user)
        request.header_data = ReportHeaderBase(
            **header_data.dict(),
            user_id=user.id
        )
        parser_data = self.__get_parser_data(request, session)

        return Parser()(parser_data)

    def __get_parser_data(self, request: i.IRequest,
                          session: Session) -> ParserData:
        """Prepare required parser data by request information."""

        header = ReportHeader(**request.header_data.dict())
        crud.add_instance(header, session)

        return ParserData(
            header_id=header.id,  # type: ignore
            products_by_url=self.__get_products_by_url(request, session),
            retailers=crud.get_retailers(request.shop_names, session),
            session=session
        )

    def __get_products_by_url(self, request: i.IRequest,
                              session: Session) -> ProductsByURL:
        """Returns products, sorted by urls."""

        pr_by_url: ProductsByURL = defaultdict(deque)
        for page in self.__get_pages(request, session):
            pr_by_url[page.url].append(page.product)  # type: ignore

        return pr_by_url

    def __get_pages(self, request: i.IRequest,
                    session: Session) -> list[WebPage]:
        """Get web pages(links), containing request products."""

        pages = []
        product_ids = {_.id for _ in request.get_products(session)}
        for rtl in request.get_retailers(session):
            query = session.query(WebPage)
            query = query.filter_by(retailer_id=rtl.id)
            query = query.filter(WebPage.product_id.in_(product_ids))
            pages.extend(query.all())

        return pages


report_mngr = ReportManager()


class TestReportManager(ReportManager):
    """Test class for report manager."""


