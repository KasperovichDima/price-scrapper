"""Core validation schamas."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

from constants import CATALOG_NAMES, RETAILER_NAMES

from project_typing import cat_elements

from pydantic import BaseModel, validator


class RequestDataScheme(BaseModel):
    """RequestData  validation scheme."""

    el_ids: cat_elements | None
    ret_names: list[str] | None

    @validator('el_ids')
    def catalog_names_alloved(cls, names: cat_elements):
        RequestDataScheme.__check_names(names, CATALOG_NAMES, 'catalog')

    @validator('ret_names')
    def retailer_names_alloved(cls, names: list[str]):
        RequestDataScheme.__check_names(names, RETAILER_NAMES, 'retailer')

    class Config:
        orm_mode = True

    @staticmethod
    def __check_names(names: Iterable[str], source: frozenset[str], type: str):
        """
        Checks, that 'type' names are in'source'. If not - raises exception.
        """
        if not names:
            return
        for name in names:
            if name not in source:
                raise ValueError(f'Incorrect {type} name: "{name}".')


class ReportHeaderScheme(BaseModel):
    """
    Validation model for completed report header.
    TODO: Add datatypes optimization.
    """

    user_name: str
    report_name: str
    report_note: str
    time_created: datetime
    retailers: list[str]


class ReportLineScheme(BaseModel):
    """Validation model for completed report line."""

    product_name: str
    prices: dict[str, tuple[float | None, float | None]]


class CompleteReportScheme(BaseModel):
    """Validation model for completed report with header and content."""

    header: ReportHeaderScheme
    content: list[ReportLineScheme]
