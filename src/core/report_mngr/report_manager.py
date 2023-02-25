"""Report manager class and instance."""
from collections import defaultdict

from authentication.models import User

import crud

from sqlalchemy.ext.asyncio import AsyncSession

from .request import Request
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
                               session: AsyncSession) -> RequestOutScheme:

        request = self.get_request(user)
        request.add_objects(await get_request_objects(in_data, session))
        return request.out_data

    async def remove_request_data(self, user: User,
                                  in_data: RequestInScheme,
                                  session: AsyncSession) -> RequestOutScheme:

        request = self.get_request(user)
        request.remove_objects(await get_request_objects(in_data, session))
        return request.out_data

    async def get_report(self, user: User,
                         header: ReportHeaderScheme,
                         session: AsyncSession):
        """Returns report, created by request parameters."""

        header.user_name = str(user)
        request = self.__requests.pop(user)
        product_ids = (_.id for _ in request.products)
        retailer_ids = (_.id for _ in request.retailers)
        price_lines = await crud.get_price_lines(prod_ids=product_ids,
                                                 ret_ids=retailer_ids,
                                                 session=session)

        return ReportScheme(
            header=header,
            folders=request.folders,
            products=request.products,
            retailers=request.retailers,
            content=price_lines
        )


report_mngr = ReportManager()
