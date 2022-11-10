"""Report router."""
from authentication.models import User

from dependencies import get_current_active_user, oauth2_scheme

from fastapi import APIRouter, Depends

from .schemas import cat_elements
from .support import report_mngr


router = APIRouter(prefix='/report', tags=['reports'])


@router.post('/add_products')
def add_products(
    products: cat_elements,
    user: User = Depends(get_current_active_user),
    token=Depends(oauth2_scheme)
):
    """Add products to report of current authorized user."""
    report_mngr.add_elements(user, products)


@router.delete('/remove_products')
def remove_products(
    products: cat_elements,
    user: User = Depends(get_current_active_user),
    token=Depends(oauth2_scheme)
):
    """Remoce products from report of current authorized user."""
    report_mngr.remove_elements(user, products)


# @router.post('/test')
# def test(
#     products: dict[str, list[int]],
#     user: User = Depends(get_current_active_user),
#     token=Depends(oauth2_scheme)
# ):
#     """just a test of validation"""
#     pass
