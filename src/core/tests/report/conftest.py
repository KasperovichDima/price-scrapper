"""Report conftest."""
import asyncio
from datetime import datetime

from authentication.models import User

from core import report_mngr
from core.core_typing import RequestObjects
from core.models import PriceLine
from core.schemas import ReportHeaderScheme, RequestInScheme

import crud

import pytest

from sqlalchemy.orm import Session


@pytest.fixture
def fake_request_data(create_fake_user: User, fake_session: Session,
                      fake_payload: RequestInScheme, fake_db_content):
    """
    Load report manager with fake request data. Autocleard after test.
    TODO: Check if we need it.
    """
    request_data = asyncio.run(report_mngr.add_request_data(create_fake_user,
                                                            fake_payload,
                                                            fake_session))
    yield request_data
    asyncio.run(report_mngr.remove_request_data(create_fake_user,
                                                fake_payload,
                                                fake_session))


@pytest.fixture
def fake_header():
    return ReportHeaderScheme(
        name='just a fake report',
        note='just a fake note',
        time_created=datetime.fromisoformat('2022-12-10T15:42:32.373798')
    )


@pytest.fixture
def fake_prices(fake_session, fake_db_content: RequestObjects):
    """Create random prices for products for retailers."""

    retail_price = 50
    promo_price = 40
    price_lines = []
    for pr in fake_db_content.products:
        for rt in fake_db_content.retailers:
            price_lines.append(
                PriceLine(
                    product_id=pr.id,
                    retailer_id=rt.id,
                    retail_price=retail_price,
                    promo_price=promo_price,
                )
            )
            retail_price += 1
            promo_price += 1

    asyncio.run(crud.add_instances(price_lines, fake_session))
    yield price_lines
    asyncio.run(crud.delete_cls_instances(price_lines, fake_session))
