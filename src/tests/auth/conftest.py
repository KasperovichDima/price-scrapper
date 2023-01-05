"""Authentication conftest."""
from authentication.models import User
from authentication.schemas import UserCreate

import crud

from project_typing import UserType

import pytest

from sqlalchemy.orm import Session


@pytest.fixture(scope='module')
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


@pytest.fixture
async def create_fake_user(fake_session: Session,
                           fake_user_data: UserCreate):
    """Creates and saves fake user to db. Deletes it after test."""
    user = User(**fake_user_data.dict())
    await crud.add_instance(user, fake_session)
    yield user
    await crud.delete_user(user.email)  # type: ignore
