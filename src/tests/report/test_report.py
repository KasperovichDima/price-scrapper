"""Report unit tests."""
import json

from authentication.models import User

from core import report_mngr
from core.schemas import RequestDataScheme

from requests import Response

from ..conftest import client


def send_request(url: str, payload: RequestDataScheme,
                 access_token) -> Response:
    """Request to '/report/add_products' endpoint with fake payload."""
    return client.post(url, data=payload.json(), headers=access_token)


class TestReport:
    """
    Test of:
    /add_request_data endpoint
    /remove_request_data endpoint
    """

    __add_url = '/report/add_request_data'
    __remove_url = '/report/remove_request_data'

    def test_add_ok(
        self,
        fake_payload: RequestDataScheme,
        create_superuser: User,
        access_token
    ):
        """Correct attempt to add products and retailers."""

        rsp = send_request(self.__add_url, fake_payload,
                           access_token)

        assert rsp.status_code == 200\
            and json.dumps(rsp.json()) == fake_payload.json()

    def test_add_duplicates(self, create_superuser: User,
                            fake_payload: RequestDataScheme):
        """Check that adding duplicating items is not possible."""

        report_mngr.add_request_data(create_superuser, fake_payload)
        report_mngr.add_request_data(create_superuser, fake_payload)
        request = report_mngr.get_request(create_superuser)

        assert fake_payload.el_ids == request.element_ids\
            and fake_payload.ret_names == request.retailer_names

    def test_remove_items_ok(self, create_superuser: User,
                             access_token, fake_payload: RequestDataScheme):
        """Correct attempt to remove items."""

        report_mngr.add_request_data(create_superuser, fake_payload)
        del_data = RequestDataScheme(
            el_ids={'Product': [3, 4, 37],
                    'Subgroup': [3, 10]},
            ret_names=['Tavria']
        )

        rsp = client.delete(self.__remove_url, data=del_data.json(),
                            headers=access_token)
        correct_response = '{"el_ids": {"Product": [1, 2, 5]'\
                           ', "Subgroup": [5]}, "ret_names": ["Silpo"]}'
        print(json.dumps(rsp.json()))
        assert rsp.status_code == 200\
            and json.dumps(rsp.json()) == correct_response

    def test_remove_not_existing_items(self,
                                       create_superuser: User,
                                       access_token,
                                       fake_payload: RequestDataScheme):
        """Attempt to remove not existing products."""

        print(fake_payload)
        report_mngr.add_request_data(create_superuser, fake_payload)
        del_data = RequestDataScheme(
            el_ids={'Product': [13, 24], "Subgroup": [22, 36, 65]},
            ret_names=['Epicentr']
        )
        rsp = client.delete(self.__remove_url, data=del_data.json(),
                            headers=access_token)
        request = report_mngr.get_request(create_superuser)

        assert rsp.status_code == 200 and\
            fake_payload.el_ids == request.element_ids\
            and fake_payload.ret_names == request.retailer_names
