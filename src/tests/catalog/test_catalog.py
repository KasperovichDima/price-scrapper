"""Catalog unit tests."""
from ..conftest import client


class TestGetContent:
    """Test of /catalog (get_content) endpoint."""

    __url = '/catalog'

    def test_get_content_ok(self, access_token, fake_db_content):
        """Correct attempt to get existing content."""

        rsp = client.get(self.__url+'/{cls_name}/1?cls=Subgroup',
                         headers=access_token)

        assert rsp.status_code == 200 and rsp.json() == fake_db_content

    def test_get_content_wrong_model(self, access_token, fake_db_content):
        """Attempt to get existing content with incorrect model."""

        rsp = client.get(self.__url+'/{cls_name}/1?cls=Gruppa',
                         headers=access_token)

        assert rsp.status_code == 404

    def test_get_content_not_exists(self, access_token, fake_db_content):
        """Attempt to get not existing content."""

        rsp = client.get(self.__url+'/{cls_name}/6?cls=Subgroup',
                         headers=access_token)

        assert rsp.status_code == 200 and rsp.json() == {
            'model': 'Subgroup',
            'content': None
        }
