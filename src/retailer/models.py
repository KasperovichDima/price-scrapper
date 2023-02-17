"""Retailer models."""
from base_models import Base

from sqlalchemy import Column, Enum, String

from .retailer_typing import RetailerName


class Retailer(Base):  # type: ignore
    """Retailer class."""
    __tablename__ = "retailer"

    name = Column(Enum(RetailerName), nullable=False)
    home_url = Column(String(100), nullable=False)

    def __repr__(self) -> str:
        return self.name.value

    def __eq__(self, __o: object) -> bool:
        return self.name is __o.name

    def __hash__(self) -> int:
        return hash(self.name)
