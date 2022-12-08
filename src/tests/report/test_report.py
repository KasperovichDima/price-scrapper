"""Report unit tests."""
from core.schemas import ReportHeaderScheme
from core.schemas import RequestInScheme

from .. import constants as c
from ..conftest import client
# from ..references import get_report_ok_ref


class TestReport:
    """Tests of /report/get_report endpoint."""

    def test_get_report_ok(self, fake_db_content, 
    fake_prices,
                           create_superuser, access_token,
                           fake_payload: RequestInScheme,
                           fake_header: ReportHeaderScheme):
        """Correct attempt to get report."""

        client.post(c.ADD_REQUEST_URL, data=fake_payload.json(),
                    headers=access_token)
        rsp = client.post('/report/get_report', data=fake_header.json(),
                          headers=access_token)

        print('\n')
        print(rsp.json())

        assert rsp.status_code == 200
            # and rsp.json() == get_report_ok_ref
