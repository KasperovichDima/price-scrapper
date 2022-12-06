"""Catalog unit tests."""
from catalog.schemas import FolderContent

from ..conftest import client


class TestGetContent:
    """Test of /catalog/folder_content endpoint."""

    __url = '/catalog/folder_content'

    def test_get_content_ok(self, access_token,
                            fake_db_content: FolderContent):
        """Correct attempt to get existing content."""

        rsp = client.get(self.__url+'/1', headers=access_token)
        ref = FolderContent(**dict(rsp.json()))

        assert rsp.status_code == 200\
            and ref.products == fake_db_content.products

    def test_get_content_not_exists(self, access_token, fake_db_content):
        """Attempt to get not existing content."""

        rsp = client.get(self.__url+'/45', headers=access_token)
        ref = FolderContent(**dict(rsp.json()))

        assert (rsp.status_code == 200
                and not ref.products
                and not ref.folders)
