"""Report router."""
from authentication.models import User
from fastapi import APIRouter, Depends
from typing import Iterable
from .schemas import AddInstanceSchema

from dependencies import get_current_active_user, get_session, oauth2_scheme


router = APIRouter(prefix='/report', tags=['reports'])


@router.post('/add_products')
def add_products(
    products: Iterable[AddInstanceSchema],
    session=Depends(get_session),
    user: User = Depends(get_current_active_user),
    token=Depends(oauth2_scheme)
):
    """Add products to report of current authorized user."""
