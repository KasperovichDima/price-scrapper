"""Retaqiler validation schemas."""
from pydantic import BaseModel

from .retailer_typing import RetailerName


class RetailerScheme(BaseModel):
    """Retiler validation schema."""

    id: int
    name: RetailerName

    class Config:
        orm_mode = True
