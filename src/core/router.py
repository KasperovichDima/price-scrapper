"""Core router."""
from authentication.models import User

from dependencies import get_current_active_user, get_db_session, oauth2_scheme

from fastapi import APIRouter, Depends

from project_typing import NameRetailPromo

from .exceptions import empty_request_exception
from .report_mngr import report_mngr
from .schemas import ReportHeaderScheme, ReportScheme
from .schemas import RequestInScheme, RequestOutScheme


router = APIRouter(prefix='/report', tags=['reports'])


@router.post('/add_request_data', response_model=RequestOutScheme)
async def add_request_data(data: RequestInScheme,
                           user: User = Depends(get_current_active_user),
                           token=Depends(oauth2_scheme),
                           session=Depends(get_db_session)):
    """Add products or retailers to report of current authorized user."""

    return await report_mngr.add_request_data(user, data, session)


@router.delete('/remove_request_data', response_model=RequestOutScheme)
async def remove_request_data(data: RequestInScheme,
                              user: User = Depends(get_current_active_user),
                              token=Depends(oauth2_scheme),
                              session=Depends(get_db_session)):
    """Remove products or retailers from report of current authorized user."""

    return await report_mngr.remove_request_data(user, data, session)


@router.post('/get_report', response_model=ReportScheme)
async def get_report(header: ReportHeaderScheme,
                     user: User = Depends(get_current_active_user),
                     token=Depends(oauth2_scheme),
                     session=Depends(get_db_session)):
    """Returns report, created by request parameters."""
    if not bool(report_mngr.get_request(user)):
        raise empty_request_exception
    return await report_mngr.get_report(user, header, session)


@router.post('/get_prices')
async def get_prices(folder_id: int,
                     retailer_id: int,
                     token=Depends(oauth2_scheme),
                     session=Depends(get_db_session)
                     ) -> list[NameRetailPromo]:
    return await report_mngr.get_prices(folder_id, retailer_id, session)
