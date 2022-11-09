"""Report manager class and instance."""
from typing import Iterable

import interfaces as i


class ReportManager(i.IReportManager):
    """Class for handling reports. Can create
    reports and perform all report operations."""


report_mngr = ReportManager()
