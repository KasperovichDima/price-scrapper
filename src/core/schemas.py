"""Core validation schamas."""
from __future__ import annotations

from collections import deque
from datetime import datetime

from catalog.schemas import ProductScheme

from project_typing import cat_elements

from pydantic import BaseModel


class RequestDataScheme(BaseModel):
    """RequestData  validation scheme."""

    el_names: cat_elements | None
    shop_names: list[str] | None

    class Config:
        orm_mode = True


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


class ParserDataScheme(BaseModel):
    """Data model for using in parser strategy."""

    header_id: int
    retailer_id: int
    prod_by_url: dict[str, deque[ProductScheme]]
