"""Retailer validation schemas."""
from pydantic import BaseModel, Field


class RetailerBase(BaseModel):
    """RetailerBase validation schema."""

    name: str = Field(max_length=50)
    home_url: str = Field(max_length=100)


class Retailer(RetailerBase):
    """Retailer validation schema."""

    id: int = Field(gt=0)
