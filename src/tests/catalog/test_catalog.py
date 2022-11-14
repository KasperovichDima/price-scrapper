"""Catalog unit tests."""
from ..conftest import client


class TestGetContent:
    """Test of /catalog/ (get_content) endpoint."""

    __url = '/catalog'

    def test_get_content_ok(self, access_token, fake_db_content: list):
        """Correct attempt to get existing content."""

        rsp = client.get(f'{self.__url}/Group/1', headers=access_token)

        assert rsp.status_code == 200 and rsp.content == fake_db_content[3:6]
