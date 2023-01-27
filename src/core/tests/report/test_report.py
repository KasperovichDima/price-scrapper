"""Report tests."""
from conftest import client

from core.schemas import ReportHeaderScheme
from core.tests import GET_REPORT_URL

from .references import get_report_ok_ref


class TestReport:
    """Tests of /report/get_report endpoint."""

    def test_get_report_ok(self, access_token,
                           fake_header: ReportHeaderScheme,
                           fake_request_data, fake_prices):
        """Correct attempt to get report."""

        response = client.post(GET_REPORT_URL, data=fake_header.json(),
                               headers=access_token)
        rsp_json = response.json()

        assert response.status_code == 200
        params = 'header folders products products retailers content'.split()
        for _ in params:
            assert rsp_json[_] == get_report_ok_ref[_]
