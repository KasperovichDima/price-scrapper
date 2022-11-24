"""Base parsing strategy."""
from typing import Any

import interfaces as i

from ...schemas import ParserDataScheme

from report.models import ReportLine


class BaseStrategy:
    """Base strategy class."""

    def __call__(self, pars_data: ParserDataScheme) -> Any:
        """
        Starts the parsing process using the pars_data.
        Returns report data for current retailer.
        """
        