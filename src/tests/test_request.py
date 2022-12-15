"""Report unit tests."""
from core.schemas import RequestInScheme

from requests import Response

from . import constants as c
from .conftest import client
from .references.references import add_ok_ref, remove_items_ok_ref


def send_add_request(url: str, payload: RequestInScheme,
                     access_token) -> Response:
    """Request to '/report/add_products' endpoint with fake payload."""
    return client.post(url, data=payload.json(), headers=access_token)


class TestReport:
    """
    Test of:
    /add_request_data endpoint
    /remove_request_data endpoint
    """

    def test_add_ok(self, fake_db_content, fake_payload,
                    create_superuser, access_token):
        """Correct attempt to add products and retailers."""

        rsp = send_add_request(c.ADD_REQUEST_URL, fake_payload,
                               access_token)

        assert rsp.status_code == 200\
            and rsp.json()['folders'] == add_ok_ref['folders']\
            and rsp.json()['products'] == add_ok_ref['products']\
            and rsp.json()['retailers'] == add_ok_ref['retailers']

    def test_add_duplicates(self, fake_db_content, fake_payload,
                            create_superuser, access_token):
        """Check that adding duplicating items is not possible."""

        send_add_request(c.ADD_REQUEST_URL, fake_payload, access_token)
        rsp = send_add_request(c.ADD_REQUEST_URL, fake_payload,
                               access_token)

        assert rsp.status_code == 200\
            and rsp.json()['folders'] == add_ok_ref['folders']\
            and rsp.json()['products'] == add_ok_ref['products']\
            and rsp.json()['retailers'] == add_ok_ref['retailers']

    def test_remove_items_ok(self, fake_db_content, fake_payload,
                             create_superuser, access_token):
        """Correct attempt to remove items."""

        send_add_request(c.ADD_REQUEST_URL, fake_payload, access_token)
        del_data = RequestInScheme(folders=[3, 10], products=[3, 4, 37],
                                   retailers=[1])
        rsp = client.delete(c.REMOVE_REQUEST_URL, data=del_data.json(),
                            headers=access_token)
        assert rsp.status_code == 200\
            and rsp.json()['folders'] == remove_items_ok_ref['folders']\
            and rsp.json()['products'] == remove_items_ok_ref['products']\
            and rsp.json()['retailers'] == remove_items_ok_ref['retailers']

    def test_remove_not_existing_items(self, fake_db_content, fake_payload,
                                       create_superuser, access_token):
        """Attempt to remove not existing products."""

        send_add_request(c.ADD_REQUEST_URL, fake_payload, access_token)
        del_data = RequestInScheme(
            folders=[22, 36, 65],
            products=[13, 24],
            retailers=[3]
        )
        rsp = client.delete(c.REMOVE_REQUEST_URL, data=del_data.json(),
                            headers=access_token)

        assert rsp.status_code == 200\
            and rsp.json()['folders'] == add_ok_ref['folders']\
            and rsp.json()['products'] == add_ok_ref['products']\
            and rsp.json()['retailers'] == add_ok_ref['retailers']
