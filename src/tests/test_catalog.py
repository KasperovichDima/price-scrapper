"""Catalog unit tests."""
from core.core_typing import RequestObjects

from .conftest import client
from .references.references import get_content_ok_ref


class TestGetContent:
    """Test of /catalog/folder_content endpoint."""

    __url = '/catalog/folder_content'

    def test_get_content_ok(self, access_token,
                            fake_db_content: RequestObjects):
        """Correct attempt to get existing content."""

        rsp = client.get(self.__url+'/1', headers=access_token)

        assert rsp.status_code == 200\
            and rsp.json()['products'] == get_content_ok_ref['products']

    def test_get_content_not_exists(self, access_token, fake_db_content):
        """Attempt to get not existing content."""

        rsp = client.get(self.__url+'/45', headers=access_token)

        assert (rsp.status_code == 200
                and not rsp.json()['products']
                and not rsp.json()['folders'])
