"""
Report unit tests.
"""
from authentication.models import User
from authentication.schemas import UserCreate

from report.schemas import AddInstanceSchema
from report.support import report_mngr

from ..conftest import client
import json


class TestReportCreate:
    """Test of '/report/add_products' endpoint."""

    __url = '/report/add_products'

    def test_add_product_ok(
        self,
        fake_products,
        create_superuser: UserCreate,
        access_token
    ):
        """Correct attempt to add products."""

        user = User(**create_superuser.dict())
        rsp = client.post(self.__url, json.dumps(fake_products),
                          headers=access_token)
        assert rsp.status_code == 200
        # assert report_mngr.get_products(user)
