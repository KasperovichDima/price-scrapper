"""Core models."""
from database.config import Base

from sqlalchemy import Column, ForeignKey, Integer, Numeric


class PriceLine(Base):
    """Represents prices of concrete product in concrete retailer's shop."""

    __tablename__ = 'price_line'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(ForeignKey('product.id'))
    retailer_id = Column(ForeignKey('retailer.id'))

    retail_price = Column(Numeric(scale=2))
    promo_price = Column(Numeric(scale=2))
