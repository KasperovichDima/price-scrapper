"""Report manager class and instance."""
from typing import Iterable

from report.schemas import AddInstanceSchema

import interfaces as i


class ReportManager(i.IReportManager):
    """Class for handling reports. Can create
    reports and perform all report operations."""

    def add_products(self, user: i.IUser,
                     products: Iterable[AddInstanceSchema]):
        print('\n', user)
        print(products)

    def get_products(self, user: i.IUser) -> list:
        ...


report_mngr = ReportManager()
