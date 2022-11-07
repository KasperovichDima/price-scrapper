"""Unit tests."""
from authentication.models import User
from authentication.schemas import UserCreate
from authentication.utils import create_access_token

from fastapi.testclient import TestClient

from main import app

import pytest

import crud


client = TestClient(app)


fake_user_data = UserCreate(
    first_name='Alexei',
    last_name='Holubaev',
    email='netpustote@gmail.com',
    is_active=True,
    password='alex1986')


token = 'Bearer ' + create_access_token({'sub': 'dima@ukr.net'})


def test_get_current_user_ok():
    """
    Attempt to get current user with correct token.
    TODO: Make fixture with fake user.
    """
    token_auth = {"Authorization": token}
    response = client.get(url='/auth/current_user', headers=token_auth)
    assert response.status_code == 200\
        and response.json()['email'] == 'dima@ukr.net'\
        and response.json()['last_name'] == 'Kasperovich'


def test_get_current_user_unauthorized():
    """Attempt to get current user info withiout authebntication."""
    response = client.get('/auth/current_user')
    assert response.status_code == 401


def test_create_user_ok():
    """TODO: Add fixtures."""
    # user = crud. User(**fake_user_data.dict())
    resp = client.post('/auth/create_user', data=fake_user_data.json())
    print(resp.json()['email'])
    assert resp.json()['email'] == 'netpustote@gmail.com'


if __name__ == "__main__":
    pytest.main()
