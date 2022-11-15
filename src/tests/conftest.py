"""Fixtures for authentication tests."""
from authentication.models import User
from authentication.schemas import UserCreate, UserScheme
from authentication.utils import create_access_token

from catalog.models import Group, Product

import crud

from database import Base, test_engine

from dependencies import get_session, get_test_session

from fastapi.testclient import TestClient

from main import app

from project_typing import UserType

import pytest

from report.schemas import RequestDataScheme


target_metadata = Base.metadata
target_metadata.create_all(test_engine)

app.dependency_overrides[get_session] = get_test_session

client = TestClient(app)


@pytest.fixture(scope='module')
def superuser_data():
    """Fake data for superuser creation."""
    return UserCreate(
        first_name='Dima',
        last_name='Kasperovich',
        email='dima@ukr.net',
        is_active=True,
        password='dima1987',
        type=UserType.SUPERUSER
    )


@pytest.fixture(scope='module')
def create_superuser(superuser_data: UserCreate):
    """Create and save superuser."""
    rsp = client.post('/auth/create_user', data=superuser_data.json())
    rsp_json = rsp.json()
    yield User(**superuser_data.dict())
    client.delete('/auth/delete_user', params={'email': rsp_json['email']})


@pytest.fixture(scope='module')
def fake_user_data() -> UserCreate:
    """Fake data for test user creation."""
    return UserCreate(
        first_name='Alexei',
        last_name='Holubaev',
        email='netpustote@gmail.com',
        is_active=True,
        password='alex1986'
    )


@pytest.fixture
def create_fake_user(fake_user_data: UserCreate) -> UserScheme:
    """Create fake user in database."""
    rsp = client.post('/auth/create_user', data=fake_user_data.json())
    return UserScheme(**rsp.json())


@pytest.fixture
def del_fake_user(fake_user_data: UserCreate):
    """Delete fake user from database."""
    yield
    client.delete('/auth/delete_user', params={'email': fake_user_data.email})


@pytest.fixture(scope='module')
def access_token(superuser_data: UserCreate) -> dict:
    """Get access token for tests."""
    token = 'Bearer ' + create_access_token({'sub': superuser_data.email})
    return {"Authorization": token}


@pytest.fixture(scope='module')
def fake_payload() -> RequestDataScheme:
    """Fake request payload."""

    return RequestDataScheme(
        elements={
            'Product': [1, 2, 3, 4, 5],
            'Group': [3, 5, 10]
        },
        retailers=['silpo', 'tavria']
    )


@pytest.fixture(scope='session')
def fake_session():
    from database import TestSession
    return TestSession()


@pytest.fixture(scope='session')
def fake_db_content(fake_session):
    """Fill database catalog with fake content."""
    content = [
        Group(name='Alcohol'),
        Group(name='Grocery'),
        Group(name='Milk')
    ]

    content.extend((
        Product(name='Beer Chernigovskoe 0,5', group_id=1),
        Product(name='Vine Cartuli Vazi 0,7', group_id=1),
        Product(name='Vodka Finlandia 0,7', group_id=1),
        Product(name='Sunflower Oil 1l', group_id=2),
        Product(name='Chips 500 gr', group_id=2),
        Product(name='Sugar 1kg', group_id=2),
        Product(name='Milk 1l', group_id=3),
        Product(name='Jogurt Fructegut 400ml', group_id=3),
        Product(name='Spred 200gr', group_id=3),
    ))

    crud.add_instances(content, fake_session)

    td = [{'group_id': item.group_id, 'name': item.name, 'id': item.id}
          for item in content[3:6]]
    return td
