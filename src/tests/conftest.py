"""Fixtures for authentication tests."""
from authentication.schemas import UserCreate, UserScheme
from authentication.utils import create_access_token

import crud

from project_typing import UserType

import pytest

from fastapi.testclient import TestClient

from main import app

from dependencies import get_session, get_test_session


app.dependency_overrides[get_session] = get_test_session


client = TestClient(app)


@pytest.fixture(scope='module')
def superuser_data() -> UserCreate:
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


@pytest.fixture(scope='module')
def access_token(superuser_data: UserCreate) -> dict:
    """Get access token for tests."""
    token = 'Bearer ' + create_access_token({'sub': superuser_data.email})
    return {"Authorization": token}
