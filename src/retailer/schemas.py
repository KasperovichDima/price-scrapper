"""Retaqiler validation schemas."""
from pydantic import BaseModel


class RetailerScheme(BaseModel):
    """Retiler validation schema."""

    id: int
    name: str

    class Config:
        orm_mode = True
