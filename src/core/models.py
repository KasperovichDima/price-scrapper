"""Core models."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from database import Base, int_fk

from project_typing import PriceTuple

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column  # type: ignore
from sqlalchemy.sql import functions


class PriceLine(Base):
    """Represents prices of concrete product in concrete retailer's shop."""

    __tablename__ = 'price_line'

    product_id: Mapped[int_fk] = mapped_column(ForeignKey('product.id'))
    retailer_id: Mapped[int_fk] = mapped_column(ForeignKey('retailer.id'))

    retail_price: Mapped[Decimal] = mapped_column(Numeric(scale=2))
    promo_price: Mapped[Decimal] = mapped_column(Numeric(scale=2),
                                                 nullable=True)

    date_created: Mapped[date] = mapped_column(
        server_default=functions.current_date()
    )

    @classmethod
    def from_tuple(cls, record: PriceTuple) -> PriceLine:
        return cls(
            product_id=record[0],
            retailer_id=record[1],
            retail_price=record[2],
            promo_price=record[3],
        )
    
    def as_tuple(self) -> tuple[int_fk, int_fk, Decimal, Decimal]:
        return (self.product_id, self.retailer_id,
                self.retail_price, self.promo_price)

    def __eq__(self, __o: object) -> bool:
        return self.as_tuple() == __o.as_tuple()

    def __repr__(self) -> str:
        return ('PriceLine >> prod_id: {}, ret_id: {}, '
                'retail: {}, promo: {}, created: {}.'
                .format(self.product_id, self.retailer_id, self.retail_price,
                        self.promo_price, self.date_created))
