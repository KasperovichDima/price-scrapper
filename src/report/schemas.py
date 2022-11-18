"""
Report validation schames.
"""
from __future__ import annotations

from datetime import datetime

from project_typing import cat_elements

from pydantic import BaseModel, Field


class ReportHeaderBase(BaseModel):
    """BaseReportHeader validation scheme."""

    time_created: datetime
    name: str = Field(max_length=100)
    note: str = Field(max_length=250)
    user_id: int = Field(gt=0)


class ReportHeaderScheme(ReportHeaderBase):
    """ReportHeader validation scheme."""

    id: int = Field(gt=0)
    content: list[ReportLineScheme]


class ReportLineBase(BaseModel):
    """BaseReportLine validation scheme."""

    header_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    shop_id: int = Field(gt=0)
    retail_price: float = Field(gt=0)
    promo_price: float = Field(gt=0)


class ReportLineScheme(ReportLineBase):
    """ReportLine validation scheme."""

    id: int = Field(gt=0)
    header: ReportHeaderScheme


class RequestDataScheme(BaseModel):
    """RequestData  validation scheme."""

    elements: cat_elements | None
    retailers: list[str] | None

    class Config:
        orm_mode = True
