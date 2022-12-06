"""Core models."""
from models import BaseWithID

from sqlalchemy import Column, ForeignKey, Numeric


class PriceLine(BaseWithID):
    """Represents prices of concrete product in concrete retailer's shop."""

    __tablename__ = 'price_line'

    product_id = Column(ForeignKey('product.id'))
    retailer_id = Column(ForeignKey('retailer.id'))

    retail_price = Column(Numeric(scale=2))
    promo_price = Column(Numeric(scale=2))
