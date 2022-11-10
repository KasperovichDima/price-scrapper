"""
Report unit tests.
"""
from json import dumps

from authentication.models import User
from authentication.schemas import UserCreate

from report.schemas import AddInstanceSchema
from report.support import report_mngr

from requests import Response

from ..conftest import client


def get_reference(f_products: list[dict]) -> dict:
    """Get reference add_products payload to check in assert."""
    return {product['class_name']: product['ids']
            for product in f_products}


def add_products(url: str, fake_products: list[dict],
                 access_token) -> Response:
    """Request to '/report/add_products' endpoint with fake payload."""
    return client.post(url, dumps(fake_products), headers=access_token)


def get_user(user_data: UserCreate) -> User:
    """Create and return user by create data."""
    return User(**user_data.dict())


class TestReportAddProducts:
    """Test of '/report/add_products' endpoint."""

    __url = '/report/add_products'

    def test_add_product_ok(
        self,
        fake_products: list[dict],
        create_superuser: UserCreate,
        access_token
    ):
        """Correct attempt to add products."""

        user = get_user(create_superuser)
        rsp = add_products(self.__url, fake_products,
                           access_token)
        result = report_mngr.get_elements(user)
        reference = get_reference(fake_products)

        assert rsp.status_code == 200 and reference == result

    def test_double_add_products(self, create_superuser,
                                 fake_products: list[dict]):
        """Check that adding duplicating elements is not possible."""

        user = get_user(create_superuser)
        elements = [AddInstanceSchema(class_name=_['class_name'], ids=_['ids'])
                    for _ in fake_products]
        report_mngr.add_elements(user, elements)
        reference = get_reference(fake_products)
        assert report_mngr.get_elements(user) == reference
