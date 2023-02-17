"""Retailer models."""
from database import Base

from exceptions import EqCompareError

from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column  # type: ignore

from .retailer_typing import RetailerName


class Retailer(Base):
    """Retailer class."""
    __tablename__ = "retailer"

    name: Mapped[RetailerName]
    home_url: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return self.name.value

    def __eq__(self, __o: object) -> bool:
        try:
            return self.name is __o.name  # type: ignore
        except AttributeError:
            raise EqCompareError(self, __o)

    def __hash__(self) -> int:
        return hash(self.name)
