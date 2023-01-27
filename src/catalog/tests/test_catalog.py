"""Catalog tests."""
from catalog.models import Folder

from core.core_typing import RequestObjects

import crud

import pytest

from conftest import client

from . import references as r


class TestCatalog:
    """Test of /catalog/ endpoints."""

    __get_url = '/catalog/folder_content/'
    __del_url = '/catalog/delete_folder/'

    def test_get_content_ok(self, access_token,
                            fake_db_content: RequestObjects):
        """Correct attempt to get existing content."""

        response = client.get(self.__get_url + '1', headers=access_token)
        assert response.status_code == 200\
            and response.json()['products'] == r.get_content_ok_ref['products']

    def test_get_content_not_exists(self, access_token, fake_db_content):
        """Attempt to get not existing content."""

        response = client.get(self.__get_url + '45', headers=access_token)
        assert response.status_code == 200\
            and not response.json()['products']\
            and not response.json()['folders']

    @pytest.mark.asyncio
    async def test_del_folder_ok(self, access_token, fake_session,
                                 fake_db_del_content: list[Folder]):
        """Correct attempt to delete folder. Cant
        test delete products because of SQLite PRAGMA."""
        del_id = 3
        del_folders_num = 3

        response = client.delete(self.__del_url + str(del_id),
                                 headers=access_token)
        folders = await crud.get_folders(fake_session)

        assert response.status_code == 200\
            and response.json() == del_id\
            and len(folders) == len(fake_db_del_content) - del_folders_num
