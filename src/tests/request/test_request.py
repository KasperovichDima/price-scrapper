"""Request tests."""
from core.schemas import RequestInScheme

from pydantic import BaseModel

from . import references as r
from .. import constants as c
from ..conftest import client


class TestRequest:
    """
    Test of:
    /add_request_data endpoint
    /remove_request_data endpoint
    """

    @staticmethod
    def get_add_response(payload: BaseModel, access_token):
        return client.post(c.ADD_REQUEST_URL, data=payload.json(),
                           headers=access_token)

    @staticmethod
    def get_remove_response(payload, access_token):
        return client.delete(c.REMOVE_REQUEST_URL, data=payload.json(),
                             headers=access_token)

    def test_add_request_ok(self, access_token, fake_payload, fake_db_content):
        """Correct attempt to add request data."""

        response = self.get_add_response(fake_payload, access_token)
        rsp_json = response.json()

        assert response.status_code == 200\
            and rsp_json['folders'] == r.add_request_ok_ref['folders']\
            and rsp_json['products'] == r.add_request_ok_ref['products']\
            and rsp_json['retailers'] == r.add_request_ok_ref['retailers']

    def test_add_duplicates(self, fake_payload, access_token, fake_db_content):
        """Check that adding duplicating items is not possible."""

        self.get_add_response(fake_payload, access_token)
        response = self.get_add_response(fake_payload, access_token)
        rsp_json = response.json()

        assert response.status_code == 200\
            and rsp_json['folders'] == r.add_request_ok_ref['folders']\
            and rsp_json['products'] == r.add_request_ok_ref['products']\
            and rsp_json['retailers'] == r.add_request_ok_ref['retailers']

    def test_remove_request_ok(self, fake_payload, access_token,
                               fake_db_content):
        """Correct attempt to remove items from request."""

        self.get_add_response(fake_payload, access_token)
        del_payload = RequestInScheme(folders=[3, 10], products=[3, 4, 37],
                                      retailers=[1])
        response = self.get_remove_response(del_payload, access_token)
        rsp_json = response.json()

        assert response.status_code == 200\
            and rsp_json['folders'] == r.remove_items_ok_ref['folders']\
            and rsp_json['products'] == r.remove_items_ok_ref['products']\
            and rsp_json['retailers'] == r.remove_items_ok_ref['retailers']

    def test_remove_not_existing_items(self, fake_payload, access_token,
                                       fake_db_content):
        """Attempt to remove not existing products."""

        self.get_add_response(fake_payload, access_token)
        del_payload = RequestInScheme(folders=[22, 36, 65],
                                      products=[13, 24],
                                      retailers=[3])
        response = self.get_remove_response(del_payload, access_token)
        rsp_json = response.json()

        assert response.status_code == 200\
            and rsp_json['folders'] == r.add_request_ok_ref['folders']\
            and rsp_json['products'] == r.add_request_ok_ref['products']\
            and rsp_json['retailers'] == r.add_request_ok_ref['retailers']
