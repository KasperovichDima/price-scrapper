"""Retailer models."""
from sqlalchemy import Column, Integer, String

from ...config import Base


class Retailer(Base):
    """Retailer class."""
    __tablename__ = "retailer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    home_url = Column(String(100))