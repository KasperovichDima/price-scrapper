"""Retailer models."""
from sqlalchemy import Column, Integer, String

from ...config import Base


class Retailer(Base):  # type: ignore
    """Retailer class."""
    __tablename__ = "retailer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    home_url = Column(String(100))

    def __repr__(self) -> str:
        return self.name  # type: ignore
