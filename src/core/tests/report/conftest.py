"""Report conftest."""
import asyncio
from datetime import datetime

from authentication.models import User

from core import report_mngr
from core.core_typing import RequestObjects
from core.models import PriceLine
from core.schemas import ReportHeaderScheme, RequestInScheme

import crud

from database import TestSession

import pytest
import pytest_asyncio

from sqlalchemy.orm import Session


@pytest_asyncio.fixture
async def fake_request_data(create_fake_user: User,
                            fake_payload: RequestInScheme,
                            fake_db_content):
    """
    Load report manager with fake request data. Autocleard after test.
    TODO: Check if we need it.
    """
    async with TestSession() as test_session:
        request_data = await report_mngr.add_request_data(
            create_fake_user,
            fake_payload,
            test_session
        )
        yield request_data
        await report_mngr.remove_request_data(
            create_fake_user,
            fake_payload,
            test_session
        )


@pytest.fixture
def fake_header():
    return ReportHeaderScheme(
        name='just a fake report',
        note='just a fake note',
        time_created=datetime.fromisoformat('2022-12-10T15:42:32.373798')
    )


@pytest_asyncio.fixture
async def fake_prices(fake_db_content: RequestObjects):
    """Create random prices for products for retailers."""

    retail_price = 50
    promo_price = 40
    price_lines = []
    for pr in fake_db_content.products:
        for rt in fake_db_content.retailers:
            line = PriceLine(
                product_id=pr.id,
                retailer_id=rt.id,
                retail_price=retail_price,
                promo_price=promo_price
            )
            price_lines.append(line)
            retail_price += 1
            promo_price += 1

    async with TestSession() as test_session:
        await crud.add_instances(price_lines, test_session)
        await test_session.commit()
        yield price_lines

        await crud.delete_cls_instances(price_lines, test_session)
        await test_session.commit()
