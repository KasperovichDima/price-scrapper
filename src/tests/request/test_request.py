"""Request tests."""
from ..conftest import client


class TestRequest:
    """
    Test of:
    /add_request_data endpoint
    /remove_request_data endpoint
    """

    @staticmethod
    def get_response(payload, access_token):
        return client.post(url, data=payload.json(), headers=access_token)