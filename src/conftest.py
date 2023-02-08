"""Base conftest file."""
import asyncio

from authentication.models import User
from authentication.schemas import UserCreate
from authentication.utils import create_access_token

from catalog.models import Folder, Product

from core.core_typing import RequestObjects
from core.schemas import RequestInScheme

import crud

from database import Base, TestSession, test_engine

from dependencies import get_session, get_test_session

from fastapi.testclient import TestClient

from main import app

from project_typing import ElType, UserType

import pytest

from retailer.models import Retailer
from retailer.retailer_typing import RetailerName

from sqlalchemy.orm import Session


target_metadata = Base.metadata  # type: ignore
target_metadata.create_all(test_engine)

app.dependency_overrides[get_session] = get_test_session

client = TestClient(app)


@pytest.fixture(scope='session')
def fake_user_data():
    """Fake data for user creation."""
    return UserCreate(
        first_name='Dima',
        last_name='Kasperovich',
        email='dima@ukr.net',
        password='dima1987',
    )


@pytest.fixture(scope='session')
def create_user_data():
    """Fake data for user creation."""
    return UserCreate(
        first_name='Alexei',
        last_name='Holubaev',
        email='lesha@ukr.net',
        password='lesha1986',
    )


@pytest.fixture(scope='session')
def create_fake_user(fake_session: Session,
                     fake_user_data: UserCreate):
    """Creates and saves fake user to db. Deletes it after test."""
    user = User(**fake_user_data.dict())
    user.is_active = True
    user.type = UserType.USER
    asyncio.run(crud.add_instance(user, fake_session))
    yield user

    asyncio.run(crud.delete_user(user.email, fake_session))  # type: ignore


@pytest.fixture(scope='session')
def fake_session():
    return TestSession()


@pytest.fixture(scope='session')
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


@pytest.fixture
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
            Retailer(name=RetailerName.TAVRIA, home_url='https://www.tavriav.ua/'),  # noqa: E501
            Retailer(name=RetailerName.SILPO, home_url='https://shop.silpo.ua/'),  # noqa: E501
            Retailer(name=RetailerName.EPICENTR, home_url='https://epicentrk.ua/shop/'),  # noqa: E501
        ],
    )

    asyncio.run(crud.add_instances((*content.folders, *content.products,
                                    *content.retailers), fake_session))
    yield content
    for container in content:
        asyncio.run(crud.delete_cls_instances(container, fake_session))
