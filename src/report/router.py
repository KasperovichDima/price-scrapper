"""Report router."""
from authentication.models import User
from fastapi import APIRouter, Depends
from typing import Iterable
from .schemas import AddInstanceSchema
from .support import report_mngr
from dependencies import get_current_active_user, oauth2_scheme


router = APIRouter(prefix='/report', tags=['reports'])


@router.post('/add_products')
def add_products(
    products: list[AddInstanceSchema],
    user: User = Depends(get_current_active_user),
    token=Depends(oauth2_scheme)
):
    """Add products to report of current authorized user."""
    report_mngr.add_products(user, products)
