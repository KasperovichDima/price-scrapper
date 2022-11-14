"""Report unit tests."""
from authentication.models import User

from report.schemas import RequestDataScheme
from report.support import report_mngr

from requests import Response

from ..conftest import client


def send_request(url: str, payload: RequestDataScheme,
                 access_token) -> Response:
    """Request to '/report/add_products' endpoint with fake payload."""
    return client.post(url, data=payload.json(), headers=access_token)


class TestEditReport:
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

        assert rsp.status_code == 200 and rsp.json() == fake_payload.dict()

    def test_add_duplicates(self, create_superuser: User,
                            fake_payload: RequestDataScheme):
        """Check that adding duplicating items is not possible."""

        report_mngr.add_request_data(create_superuser, fake_payload)
        report_mngr.add_request_data(create_superuser, fake_payload)

        assert fake_payload == report_mngr.get_request(create_superuser)

    def test_remove_items_ok(self, create_superuser: User,
                             access_token, fake_payload: RequestDataScheme):
        """Correct attempt to remove items."""

        report_mngr.add_request_data(create_superuser, fake_payload)
        del_data = RequestDataScheme(
            elements={'Product': [3, 4, 37],
                      'Group': [3, 10]},
            retailers=['tavria']
        )

        rsp = client.delete(self.__remove_url, data=del_data.json(),
                            headers=access_token)
        request = report_mngr.get_request(create_superuser)

        assert rsp.status_code == 200\
            and request.elements == {
                'Product': [1, 2, 5],
                'Group': [5],
            }\
            and request.retailers == ['silpo']

    def test_remove_not_existing_items(self,
                                       create_superuser: User,
                                       access_token,
                                       fake_payload: RequestDataScheme):
        """Attempt to remove not existing products."""

        report_mngr.add_request_data(create_superuser, fake_payload)
        del_data = RequestDataScheme(
            elements={'Product': [13, 24], "Category": [22, 36, 65]},
            retailers=['epicentr', 'santim']
        )
        rsp = client.delete(self.__remove_url, data=del_data.json(),
                            headers=access_token)
        request = report_mngr.get_request(create_superuser)

        assert rsp.status_code == 200 and\
            request == fake_payload
