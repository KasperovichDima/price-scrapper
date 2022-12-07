"""Report unit tests."""
from core.schemas import ReportHeaderScheme
from core.schemas import RequestInScheme

from .. import constants as c
from ..conftest import client
from ..references import get_report_ok_ref


class TestReport:
    """Tests of /get_report endpoint."""

    def test_get_report_ok(self, header: ReportHeaderScheme,
                           fake_payload: RequestInScheme, access_token):
        """Correct attempt to get report."""

        client.post(c.ADD_REQUEST_URL, data=fake_payload.json(),
                    headers=access_token)
        rsp = client.post(c.GET_REPORT_URL, data=header.json(),
                          headers=access_token)

        assert rsp.status_code == 200\
            and rsp.json() == get_report_ok_ref
