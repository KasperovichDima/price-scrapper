"""
Report unit tests.
"""
from authentication.models import User
from authentication.schemas import UserCreate

from report.schemas import cat_elements
from report.support import report_mngr

from requests import Response

from ..conftest import client


def add_products(url: str, fake_products: cat_elements,
                 access_token) -> Response:
    """Request to '/report/add_products' endpoint with fake payload."""
    return client.post(url, json=fake_products, headers=access_token)


def get_user(user_data: UserCreate) -> User:
    """Create and return user by create data."""
    return User(**user_data.dict())


class TestReportAddProducts:
    """Test of '/report/add_products' endpoint."""

    __url = '/report/add_products'

    def test_add_product_ok(
        self,
        fake_products: cat_elements,
        create_superuser: UserCreate,
        access_token
    ):
        """Correct attempt to add products."""

        user = get_user(create_superuser)
        rsp = add_products(self.__url, fake_products,
                           access_token)
        result = report_mngr.get_elements(user)

        assert rsp.status_code == 200 and fake_products == result

    def test_double_add_products(self, create_superuser,
                                 fake_products: cat_elements):
        """Check that adding duplicating elements is not possible."""

        user = get_user(create_superuser)
        report_mngr.add_elements(user, fake_products)

        assert report_mngr.get_elements(user) == fake_products


class TestReportRemoveProducts:
    """Test of '/report/remove_products' endpoint."""

    __url = '/report/remove_products'

    def test_remove_products_ok(self, create_superuser, access_token,
                                fake_products: cat_elements):
        """Correct attempt to remove products."""

        user = get_user(create_superuser)
        report_mngr.add_elements(user, fake_products)
        del_data = {'Product': [3, 4]}
        rsp = client.delete(self.__url, json=del_data,
                            headers=access_token)
        print(report_mngr.get_elements(user))

        assert rsp.status_code == 200 and\
            report_mngr.get_elements(user) == {
                'Product': [1, 2, 5],
                'Group': [3, 5, 10]
            }
