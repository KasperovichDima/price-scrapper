"""Retailer models."""
from base_models import BaseWithID

from project_typing import RetailerName

from sqlalchemy import Column, Enum, String


class Retailer(BaseWithID):  # type: ignore
    """Retailer class."""
    __tablename__ = "retailer"

    name = Column(Enum(RetailerName), nullable=False)
    home_url = Column(String(100), nullable=False)

    def __repr__(self) -> str:
        return self.name.value
