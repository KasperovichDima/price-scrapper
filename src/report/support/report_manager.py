"""Report manager class and instance."""
from typing import Iterable

import interfaces as i

from report.schemas import AddInstanceSchema


class ReportManager(i.IReportManager):
    """Class for handling reports. Can create
    reports and perform all report operations."""

    def add_products(self, user: i.IUser,
                     products: Iterable[AddInstanceSchema]):
        ...

    def get_products(self, user: i.IUser) -> list:
        ...


report_mngr = ReportManager()
