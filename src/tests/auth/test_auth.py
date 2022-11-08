"""
Authentication unit tests.
TODO: Inmemory db for tests.
"""
from authentication.schemas import UserCreate, UserScheme

from ..conftest import client

import pytest


class TestGetCurrentUser:
    """Test of '/auth/current_user' endpoint."""

    def test_get_current_user_ok(self, create_superuser: UserScheme,
                                 access_token: dict):
        """
        Attempt to get current user with correct token.
        TODO: Make fixture with fake user.
        """
        response = client.get(url='/auth/current_user', headers=access_token)
        rsp_data = response.json()
        print(create_superuser)
        assert response.status_code == 200\
            and rsp_data['email'] == create_superuser.email\
            and rsp_data['last_name'] == create_superuser.last_name

    def test_get_current_user_unauthorized(self):
        """Attempt to get current user info without authebntication."""
        response = client.get('/auth/current_user')
        assert response.status_code == 401


class TestCreateUser:
    """Test of '/auth/create_user' endpoint."""

    def test_create_user_ok(self, fake_user_data: UserCreate):
        """TODO: Add fixtures."""

        resp = client.post('/auth/create_user', data=fake_user_data.json())
        assert resp.json()['email'] == fake_user_data.email


if __name__ == "__main__":
    pytest.main()
