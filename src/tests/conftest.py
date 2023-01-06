"""Base conftest."""
from authentication.schemas import UserCreate
from authentication.utils import create_access_token

from database import Base, TestSession, test_engine

from dependencies import get_session, get_test_session

from fastapi.testclient import TestClient

from main import app

import pytest


target_metadata = Base.metadata  # type: ignore
target_metadata.create_all(test_engine)

app.dependency_overrides[get_session] = get_test_session

client = TestClient(app)


@pytest.fixture(scope='module')
def fake_session():
    return TestSession()


@pytest.fixture(scope='module')
def access_token(fake_user_data: UserCreate):
    """Get access token for tests."""
    token = 'Bearer ' + create_access_token({'sub': fake_user_data.email})
    return {'Authorization': token}
