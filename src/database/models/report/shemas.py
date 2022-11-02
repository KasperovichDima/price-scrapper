"""Report validation schemas."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class BaseReportHeader(BaseModel):
    """BaseReportHeader validation schema."""

    time_created: datetime
    name: str = Field(max_length=100)
    note: str = Field(max_length=250)
    user_id: int = Field(gt=0)


class ReportHeader(BaseReportHeader):
    """ReportHeader validation schema."""

    id: int = Field(gt=0)
    content: list[ReportLine]

    
class BaseReportLine(BaseModel):
    """BaseReportLine validation schema."""

    header_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    shop_id: int = Field(gt=0)
    retail_price: float = Field(gt=0)
    promo_price: float = Field(gt=0)


class ReportLine(BaseReportLine):
    """ReportLine validation schema."""
    
    id: int = Field(gt=0)
    header: ReportHeader
