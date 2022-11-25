"""Report router."""
from core import report_mngr
from core.schemas import RequestDataScheme

from dependencies import get_current_active_user, get_session, oauth2_scheme

from fastapi import APIRouter, Depends

from interfaces import IUser

from .schemas import ReportHeaderIn

from .exceptions import empty_request_exception


router = APIRouter(prefix='/report', tags=['reports'])


@router.post('/add_request_data', response_model=RequestDataScheme)
async def add_request_data(data: RequestDataScheme,
                           user: IUser = Depends(get_current_active_user),
                           token=Depends(oauth2_scheme)):
    """Add products or retailers to report of current authorized user."""

    return report_mngr.add_request_data(user, data)


@router.delete('/remove_request_data', response_model=RequestDataScheme)
async def remove_request_data(data: RequestDataScheme,
                              user: IUser = Depends(get_current_active_user),
                              token=Depends(oauth2_scheme)):
    """Remove products or retailers from report of current authorized user."""

    return report_mngr.remove_request_data(user, data)


@router.post('/get_report')
async def get_report(header_data: ReportHeaderIn,
                     user: IUser = Depends(get_current_active_user),
                     token=Depends(oauth2_scheme),
                     session=Depends(get_session)):
    """
    Start parsing process and get completed report.
    TODO: Add response model.
    """
    if not report_mngr.get_request(user):
        raise empty_request_exception

    return report_mngr.get_report(header_data, user, session)
