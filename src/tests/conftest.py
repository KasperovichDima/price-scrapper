"""Base conftest."""
import asyncio

from authentication.models import User
from authentication.schemas import UserCreate
from authentication.utils import create_access_token

import crud

from database import Base, TestSession, test_engine

from dependencies import get_session, get_test_session

from fastapi.testclient import TestClient

from main import app

from project_typing import UserType

import pytest

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
        is_active=True,
        password='dima1987',
        type=UserType.USER
    )


@pytest.fixture(scope='session')
def create_fake_user(fake_session: Session,
                     fake_user_data: UserCreate):
    """Creates and saves fake user to db. Deletes it after test."""
    print('creating fake user')
    user = User(**fake_user_data.dict())
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
