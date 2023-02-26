"""Base conftest file."""
import asyncio

from authentication.models import User
from authentication.schemas import UserCreate
from authentication.utils import create_access_token
from authentication import UserType

from catalog.models import Folder, Product

from core.core_typing import RequestObjects
from core.schemas import RequestInScheme

import crud

from database import Base, TestSession, test_engine

from dependencies import get_db_session, get_test_session

from fastapi.testclient import TestClient

from main import app

import pytest
import pytest_asyncio

from retailer.models import Retailer
from retailer.retailer_typing import RetailerName


app.dependency_overrides[get_db_session] = get_test_session


async def create_tables() -> None:
    async with test_engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)


asyncio.run(create_tables())

client = TestClient(app)


@pytest.fixture()
def fake_user_data():
    """Fake data for user creation."""
    return UserCreate(
        first_name='Dima',
        last_name='Kasperovich',
        email='dima@ukr.net',
        password='dima1987',
    )


@pytest.fixture()
def create_user_data():
    """Fake data for user creation."""
    return UserCreate(
        first_name='Alexei',
        last_name='Holubaev',
        email='lesha@ukr.net',
        password='lesha1986',
    )


@pytest_asyncio.fixture()
async def create_fake_user(fake_user_data: UserCreate):
    """Creates and saves fake user to db. Deletes it after test."""
    user = User(**fake_user_data.dict())
    user.is_active = True
    user.type = UserType.USER
    async with TestSession() as test_session:
        await crud.add_instance(user, test_session)
        await test_session.commit()
        yield user

        await crud.delete_user(user.email, test_session)
        await test_session.commit()


@pytest.fixture()
def access_token(fake_user_data: UserCreate, create_fake_user):
    """Get access token for tests."""
    token = 'Bearer ' + create_access_token({'sub': fake_user_data.email})
    return {'Authorization': token}


@pytest.fixture
def fake_payload() -> RequestInScheme:
    """Fake request payload."""

    return RequestInScheme(
        folders=[2, 3],
        products=[1, 2, 3, 4, 5, 6],
        retailers=[1, 2]
    )


@pytest_asyncio.fixture
async def fake_db_content():
    """Fill database catalog with fake content."""
    content = RequestObjects(
        [
            Folder(name='Alcohol'),
            Folder(name='Grocery'),
            Folder(name='Milk'),
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
            Retailer(name=RetailerName.TAVRIA, home_url='https://www.tavriav.ua/'),  # noqa: E501
            Retailer(name=RetailerName.SILPO, home_url='https://shop.silpo.ua/'),  # noqa: E501
            Retailer(name=RetailerName.EPICENTR, home_url='https://epicentrk.ua/shop/'),  # noqa: E501
        ],
    )

    async with TestSession() as test_session:
        await crud.add_instances((*content.folders,
                                  *content.products,
                                  *content.retailers),
                                 test_session)
        await test_session.commit()
        yield content
        for container in content:
            await crud.delete_cls_instances(container, test_session)
        await test_session.commit()
