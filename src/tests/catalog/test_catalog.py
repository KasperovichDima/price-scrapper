"""Catalog unit tests."""
from ..conftest import client


class TestGetContent:
    """Test of /catalog/ (get_content) endpoint."""

    __url = '/catalog'

    def test_get_content_ok(self, access_token, fake_db_content: list):
        """Correct attempt to get existing content."""

        rsp = client.get(self.__url+'/{cls_name}/1?cls=Group',
                         headers=access_token)

        print(type(rsp.json()))

        assert rsp.status_code == 200 and rsp.json() == fake_db_content
