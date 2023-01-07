"""Request conftest."""
import asyncio

from catalog.models import Folder, Product

from core.core_typing import RequestObjects
from core.schemas import RequestInScheme

import crud

from project_typing import ElType

import pytest

from retailer.models import Retailer


@pytest.fixture(scope='module')
def fake_db_content(fake_session):
    """Fill database catalog with fake content."""
    content = RequestObjects(
        [
            Folder(name='Alcohol', el_type=ElType.CATEGORY),
            Folder(name='Grocery', el_type=ElType.CATEGORY),
            Folder(name='Milk', el_type=ElType.CATEGORY),
        ],
        [
            Product(name='Beer Chernigovskoe 0,5', parent_id=1, prime_cost=23.5),  # noqa: E501
            Product(name='Vine Cartuli Vazi 0,7', parent_id=1, prime_cost=58.15),  # noqa: E501
            Product(name='Vodka Finlandia 0,7', parent_id=1, prime_cost=115.96),  # noqa: E501
            Product(name='Sunflower Oil 1l', parent_id=2, prime_cost=20.99),
            Product(name='Chips 500 gr', parent_id=2, prime_cost=15.20),
            Product(name='Sugar 1kg', parent_id=2, prime_cost=9.99),
            Product(name='Milk 1l', parent_id=3, prime_cost=12.35),
            Product(name='Jogurt Fructegut 400ml', parent_id=3, prime_cost=19.84),  # noqa: E501
            Product(name='Spred 200gr', parent_id=3, prime_cost=27.80),
        ],
        [
            Retailer(name='Tavria', home_url='https://www.tavriav.ua/'),
            Retailer(name='Silpo', home_url='https://shop.silpo.ua/'),
            Retailer(name='Epicentr', home_url='https://epicentrk.ua/shop/'),
        ]
    )

    asyncio.run(crud.add_instances((*content.folders, *content.products,
                                    *content.retailers), fake_session))
    yield
    for container in content:
        asyncio.run(crud.delete_cls_instances(container, fake_session))


@pytest.fixture(scope='module')
def fake_payload() -> RequestInScheme:
    """Fake request payload."""

    return RequestInScheme(
        folders=[2, 3],
        products=[1, 2, 3, 4, 5, 6],
        retailers=[1, 2]
    )
