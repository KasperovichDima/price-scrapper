"""Retailer typing."""
from __future__ import annotations

from enum import Enum


class RetailerName(Enum):
    """Available retailers"""

    TAVRIA = 'TAVRIA'
    SILPO = 'SILPO'
    EPICENTR = 'EPICENTR'

    def __lt__(self, other: RetailerName) -> bool:
        return self.value < other.value
