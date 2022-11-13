"""Report router."""
from authentication.models import User

from dependencies import get_current_active_user, oauth2_scheme

from fastapi import APIRouter, Depends

from .schemas import RequestDataScheme
from .support import report_mngr


router = APIRouter(prefix='/report', tags=['reports'])


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
