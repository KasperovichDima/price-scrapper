"""
Authentication unit tests.
TODO: Inmemory db for tests.
      Cover '/token' endpoint.
"""
from authentication.schemas import UserCreate, UserScheme

from ..conftest import client


class TestGetCurrentUser:
    """Test of '/auth/current_user' endpoint."""

    def test_get_current_user_ok(self, create_superuser: UserScheme,
                                 access_token):
        """Attempt to get current user with correct token."""

        response = client.get(url='/auth/current_user', headers=access_token)
        rsp_data = response.json()
        assert response.status_code == 200\
            and rsp_data['email'] == create_superuser.email\
            and rsp_data['last_name'] == create_superuser.last_name

    def test_get_current_user_unauthorized(self):
        """Attempt to get current user info without authebntication."""
        response = client.get('/auth/current_user')
        assert response.status_code == 401


class TestCreateUser:
    """Test of '/auth/create_user' endpoint."""

    def test_create_user_ok(self, fake_user_data: UserCreate, del_fake_user):
        """Attempt to create user with correct data."""

        resp = client.post('/auth/create_user', data=fake_user_data.json())
        assert resp.status_code == 200\
            and resp.json()['email'] == fake_user_data.email

    def test_create_duplicate_user(self, superuser_data: UserCreate):
        """Attempt to create user with existing email."""

        rsp = client.post('/auth/create_user', data=superuser_data.json())
        assert rsp.status_code == 409


class TestDeleteUser:
    """Test of '/auth/delete_user' endpoint."""

    def test_delete_user_ok(self, create_fake_user: UserScheme):
        """Attempt to delete existing user."""

        rsp = client.delete(
            '/auth/delete_user',
            params={'email': create_fake_user.email})
        assert rsp.status_code == 200\
            and rsp.json()['email'] == create_fake_user.email

    def test_delete_not_exists_user(self, fake_user_data: UserCreate):
        """Attempt to delete not existing user."""

        rsp = client.delete(
            '/auth/delete_user',
            params={'email': fake_user_data.email})
        assert rsp.status_code == 404
