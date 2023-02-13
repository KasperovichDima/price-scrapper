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
from ..catalog import Catalog
from ..price_parser import FactoryCreator
from ..price_parser import TavriaParser
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
    async def test_catalog_parser(self, fake_session,
                                  fake_catalog_db, fake_retailers):
        retailer = await crud.get_ratailer(RetailerName.TAVRIA, fake_session)
        catalog = Catalog(retailer.home_url, fake_session)
        f_creator = FactoryCreator(retailer, PriceFactory_test)
        parser = TavriaParser(catalog, f_creator)
        await parser.update_catalog()

        result_folders = await crud.get_folders(fake_session)
        result_actual_folder_names = set(_.name for _ in result_folders
                                         if not _.deprecated)
        result_deprecated_folder_names = set(_.name for _ in result_folders
                                             if _.deprecated)

        assert result_actual_folder_names == r.ref_actual_folder_names
        assert result_deprecated_folder_names == r.ref_deprecated_folder_names

    @pytest.mark.asyncio
    async def test_product_parser(self, fake_session, fake_price_lines):
        # "Distinct on" simulation
        crud.get_last_price_lines = fake_last_price_lines

        await box.initialize(fake_session)
        retailer = await crud.get_ratailer(RetailerName.TAVRIA, fake_session)
        catalog = Catalog(retailer.home_url, fake_session)
        f_creator = FactoryCreator(retailer, PriceFactory_test)
        parser = TavriaParser(catalog, f_creator)
        await parser.update_products()

        result_products = await crud.get_products(fake_session)
        result_actual_product_names = set(_.name for _ in result_products
                                          if not _.deprecated)
        result_deprecated_product_names = set(_ .name for _ in result_products
                                              if _.deprecated)

        prod_ids = [_.id for _ in result_products]
        db_prices = set(await crud.get_last_price_lines(prod_ids, 1,
                                                        fake_session))
        price_res = {(_.retailer_id, _.product_id,
                      _.retail_price, _.promo_price)
                     for _ in db_prices}
        price_ref = {(_.retailer_id,
                      _.product_id,
                      decimal.Decimal(str(_.retail_price)),
                      decimal.Decimal(str(_.promo_price))
                      if _.promo_price else None)
                     for _ in r.ref_price_lines}

        assert price_res == price_ref
        assert result_actual_product_names == r.ref_actual_product_names
        assert result_deprecated_product_names\
            == r.ref_deprecated_product_names
