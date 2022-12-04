"""Report validation schames."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ReportHeader(BaseModel):
    """Validation of required user data for report header."""

    name: str = Field(max_length=100)
    note: str = Field(max_length=250)
    time_created: datetime = datetime.now()
    user_name: str | None
