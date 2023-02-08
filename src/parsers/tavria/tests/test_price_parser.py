"""Price parser tests."""
import decimal
from typing import Iterable

from core.models import PriceLine

import crud

import pytest

from retailer.retailer_typing import RetailerName

from sqlalchemy.orm import Session

from . import reference as r
from .mock_classes import PriceFactory_test
from ..price_parser import FactoryCreator
from ..price_parser import PriceParser
from ..price_parser import box


async def fake_last_price_lines(product_ids: Iterable[int],
                                reatiler_id: int,
                                session: Session) -> list[PriceLine]:
    """Distinct on is not supported by SQLite, so we need simulation here."""
    all_lines: list[PriceLine] = session.query(PriceLine)\
        .filter(PriceLine.retailer_id == reatiler_id,
                PriceLine.product_id.in_(product_ids))\
        .order_by(PriceLine.product_id.asc())\
        .order_by(PriceLine.date_created.asc())\
        .all()
    return list({_.product_id: _ for _ in all_lines}.values())


class TestTavriaPriceParser:
    """Test class for tavria price parser."""

    @pytest.mark.asyncio
    async def test_price_parser(self, fake_session, fake_price_lines):
        # "Distinct on" simulation
        crud.get_last_price_lines = fake_last_price_lines

        await box.initialize(fake_session)
        parser = PriceParser(FactoryCreator, PriceFactory_test)
        await parser.refresh_prices(RetailerName.TAVRIA, fake_session)

        products = await crud.get_products(fake_session)
        prod_ids = [_.id for _ in products]
        results = set(await crud.get_last_price_lines(prod_ids, 1,
                                                      fake_session))
        res = {(_.retailer_id, _.product_id, _.retail_price, _.promo_price)
               for _ in results}
        ref = {(_.retailer_id,
                _.product_id,
                decimal.Decimal(str(_.retail_price)),
                decimal.Decimal(str(_.promo_price))
                if _.promo_price else None)
               for _ in r.ref_price_lines}
        assert res == ref
