"""Report router."""
from authentication.models import User

from core import report_mngr
from core.schemas import RequestDataScheme

from dependencies import get_current_active_user, oauth2_scheme

from fastapi import APIRouter, Depends

from .schemas import ReportHeaderBase


router = APIRouter(prefix='/report', tags=['reports'])


@router.post('/add_request_data', response_model=RequestDataScheme)
async def add_request_data(data: RequestDataScheme,
                           user: User = Depends(get_current_active_user),
                           token=Depends(oauth2_scheme)):
    """Add products or retailers to report of current authorized user."""

    return report_mngr.add_request_data(user, data)


@router.delete('/remove_request_data', response_model=RequestDataScheme)
async def remove_request_data(data: RequestDataScheme,
                              user: User = Depends(get_current_active_user),
                              token=Depends(oauth2_scheme)):
    """Remove products or retailers from report of current authorized user."""

    return report_mngr.remove_request_data(user, data)


# @router.post('/get_report')
# async def get_report(name: str, note: str,
#                      user: User = Depends(get_current_active_user),
#                      token=Depends(oauth2_scheme)):
#     """Start parsing process and get completed report."""

#     header_payload = ReportHeaderBase(name=name, note=note, user_id=user.id)
#     report_mngr.get_report

