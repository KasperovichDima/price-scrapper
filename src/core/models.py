"""Core models."""
from __future__ import annotations

from base_models import BaseWithID

from project_typing import PriceRecord

from sqlalchemy import Column, Date, ForeignKey, Numeric
from sqlalchemy import func


class PriceLine(BaseWithID):
    """Represents prices of concrete product in concrete retailer's shop."""

    __tablename__ = 'price_line'

    product_id = Column(ForeignKey('product.id'))
    retailer_id = Column(ForeignKey('retailer.id'))

    retail_price = Column(Numeric(scale=2))
    promo_price = Column(Numeric(scale=2))

    date_created = Column(Date(), server_default=func.now())

    @classmethod
    def from_tuple(cls, record: PriceRecord) -> PriceLine:
        return cls(
            product_id=record[0],
            retailer_id=record[1],
            retail_price=record[2],
            promo_price=record[3],
        )

    def __hash__(self) -> int:
        return hash((self.product_id, self.retailer_id,
                     self.retail_price, self.promo_price))

    def __eq__(self, __o: object) -> bool:
        return hash(self) == hash(__o)

    def __repr__(self) -> str:
        return ('PriceLine >> prod_id: {}, ret_id: {}, '
                'retail: {}, promo: {}, created: {}.'
                .format(self.product_id, self.retailer_id, self.retail_price,
                        self.promo_price, self.date_created))
