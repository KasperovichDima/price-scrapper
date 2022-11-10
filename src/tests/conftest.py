"""Fixtures for authentication tests."""
from authentication.schemas import UserCreate, UserScheme
from authentication.utils import create_access_token

from dependencies import get_session, get_test_session

from fastapi.testclient import TestClient

from main import app

from project_typing import UserType, cat_elements

import pytest


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
    yield UserScheme(**rsp_json)
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
def fake_products() -> cat_elements:
    """Fake products payload."""

    return {
        'Product': [1, 2, 3, 4, 5],
        'Group': [3, 5, 10]
    }
