"""Report manager class and instance."""
from collections import defaultdict

from authentication.models import User

import crud

from project_typing import NameRetailPromo

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
        price_lines = await crud.get_last_prices(
            session, (_.id for _ in request.retailers),
            prod_ids=(_.id for _ in request.products),
            folder_ids=(_.id for _ in request.folders),
        )

        return ReportScheme(header=header,
                            folders=request.folders,
                            products=request.products,
                            retailers=request.retailers,
                            content=price_lines)

    @staticmethod
    async def get_prices(folder_id: int,
                         retailer_id: int,
                         session: AsyncSession
                         ) -> list[NameRetailPromo]:
        """Returns product names, product retail prices,
        product promo prices for products in specified folder"""

        prices = await crud.get_last_prices(session, (retailer_id,),
                                            folder_ids=(folder_id,))
        id_to_name = {_.id: _.name for _ in await
                      crud.get_products(session, folder_ids=(folder_id,))}
        return sorted([(id_to_name[_.product_id],
                        _.retail_price,
                        _.promo_price)
                       for _ in prices], key=lambda _: _[1])


report_mngr = ReportManager()
