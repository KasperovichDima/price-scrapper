"""Authentication tests."""
from authentication.schemas import UserCreate

import pytest

from ..conftest import client


class TestCreateUser:
    """Tests of '/auth/create_user' endpoint."""

    @staticmethod
    def get_response(data: UserCreate):
        return client.post('/auth/create_user', data=data.json())

    @pytest.mark.asyncio
    async def test_create_user_ok(self, fake_user_data):
        """Attempt to create user with correct data."""

        resp = self.get_response(fake_user_data)
        assert resp.status_code == 200\
            and resp.json()['email'] == fake_user_data.email

    @pytest.mark.asyncio
    async def test_create_duplicate_user(self, fake_user_data,
                                         create_fake_user):
        """Attempt to create user with existing email."""

        resp = self.get_response(fake_user_data)
        assert resp.status_code == 409
