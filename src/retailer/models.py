"""Retailer models."""
from interfaces import IRetailer

from models import BaseWithRepr

from sqlalchemy import Column, String


class Retailer(BaseWithRepr, IRetailer):  # type: ignore
    """Retailer class."""
    __tablename__ = "retailer"

    name = Column(String(50), index=True)
    home_url = Column(String(100))
