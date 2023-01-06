"""Authentication tests."""
from authentication.models import User
from authentication.schemas import UserCreate

import pytest

from ..conftest import client


class TestCreateUser:
    """Tests of '/auth/create_user' endpoint."""

    @staticmethod
    def get_response(data: UserCreate):
        return client.post('/auth/create_user', data=data.json())

    @pytest.mark.asyncio
    async def test_create_user_ok(self, fake_user_data: UserCreate):
        """Attempt to create user with correct data."""

        resp = self.get_response(fake_user_data)
        assert resp.status_code == 200\
            and resp.json()['email'] == fake_user_data.email

    @pytest.mark.asyncio
    async def test_create_duplicate_user(self, fake_user_data,
                                         create_fake_user):
        """Attempt to create user with existing email."""

        await create_fake_user
        resp = self.get_response(fake_user_data)
        assert resp.status_code == 409


class TestGetCurrentUser:
    """Test of '/auth/current_user' endpoint."""

    @staticmethod
    def get_response(access_token):
        return client.get(url='/auth/current_user', headers=access_token)

    @pytest.mark.asyncio
    async def test_get_current_user_ok(self, access_token, create_fake_user):
        """Attempt to get current user with correct token."""
        user: User = await create_fake_user
        response = self.get_response(access_token)
        rsp_json = response.json()
        assert response.status_code == 200\
            and rsp_json['email'] == user.email
        
    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, create_fake_user):
        """Attempt to get current user info without authebntication."""
        await create_fake_user
        response = self.get_response(None)
        assert response.status_code == 401
