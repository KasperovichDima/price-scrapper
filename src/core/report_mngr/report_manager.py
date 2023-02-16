"""Report manager class and instance."""
from collections import defaultdict

from authentication.models import User

from sqlalchemy import and_
from sqlalchemy.orm import Session

from .request import Request
from ..models import PriceLine
from ..schemas import ReportHeaderScheme
from ..schemas import ReportScheme
from ..schemas import RequestInScheme
from ..schemas import RequestOutScheme
from ..utils import get_request_objects


class ReportManager:
    """
    Class for handling reports. Can create request/report and perform all
    request/report operations. Primarily - User request must be created. Every
    user has he's own request with all request parameters. Any changes will
    affect only current user request. Whem request is ready (products or/and
    folders and retailers are filled) - report can be created.
    """

    def __init__(self) -> None:
        self.__requests: defaultdict[User, Request] = defaultdict(Request)

    def get_request(self, user: User) -> Request:
        return self.__requests[user]

    async def add_request_data(self, user: User,
                               in_data: RequestInScheme,
                               session: Session) -> RequestOutScheme:

        request = self.get_request(user)
        request.add_objects(await get_request_objects(in_data, session))
        return request.out_data

    async def remove_request_data(self, user: User,
                                  in_data: RequestInScheme,
                                  session: Session) -> RequestOutScheme:

        request = self.get_request(user)
        request.remove_objects(await get_request_objects(in_data, session))
        return request.out_data

    def get_report(self, user: User,
                   header: ReportHeaderScheme,
                   session: Session):
        """
        Returns report, created by request parameters.
        TODO: Refactoring.
        """

        header.user_name = str(user)
        request = self.__requests.pop(user)
        price_lines: list[PriceLine] = session.query(PriceLine).where(
            and_(
                PriceLine.product_id.in_((_.id for _ in request.products)),
                PriceLine.retailer_id.in_((_.id for _ in request.retailers))
            )
        ).all()

        return ReportScheme(
            header=header,
            folders=request.folders,
            products=request.products,
            retailers=request.retailers,
            content=price_lines
        )


report_mngr = ReportManager()
