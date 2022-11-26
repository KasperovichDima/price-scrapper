"""Base parsing strategy."""
from typing import Any

import interfaces as i

from ...core_typing import ParserData

from report.models import ReportLine


class BaseStrategy:
    """Base strategy class."""

    def __call__(self, pars_data: ParserData) -> Any:
        """
        Starts the parsing process using the pars_data.
        Returns report data for current retailer.
        """
        