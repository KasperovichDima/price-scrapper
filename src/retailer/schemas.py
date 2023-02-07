"""Retaqiler validation schemas."""
from project_typing import RetailerName

from pydantic import BaseModel


class RetailerScheme(BaseModel):
    """Retiler validation schema."""

    id: int
    name: RetailerName

    class Config:
        orm_mode = True
