"""Report router."""
from authentication.models import User

from dependencies import get_current_active_user, oauth2_scheme

from fastapi import APIRouter, Depends

# from project_typing import cat_elements

from .support import report_mngr

from .schemas import RequestDataScheme


router = APIRouter(prefix='/report', tags=['reports'])


# @router.post('/add_products')
# def add_products(
#     products: cat_elements,
#     user: User = Depends(get_current_active_user),
#     token=Depends(oauth2_scheme)
# ):
#     """Add products to report of current authorized user."""
#     report_mngr.add_elements(user, products)


# @router.delete('/remove_products')
# def remove_products(
#     products: cat_elements,
#     user: User = Depends(get_current_active_user),
#     token=Depends(oauth2_scheme)
# ):
#     """Remove products from report of current authorized user."""
#     report_mngr.remove_elements(user, products)


@router.post('/add_request_data', response_model=RequestDataScheme)
async def add_request_data(
    data: RequestDataScheme,
    user: User = Depends(get_current_active_user),
    token=Depends(oauth2_scheme)
):
    """Add products or retailers to report of current authorized user."""

    return report_mngr.add_request_data(user, data)


@router.delete('/remove_request_data', response_model=RequestDataScheme)
async def remove_request_data(
    data: RequestDataScheme,
    user: User = Depends(get_current_active_user),
    token=Depends(oauth2_scheme)
):
    """remove products or retailers to report of current authorized user."""

    return report_mngr.remove_request_data(user, data)
