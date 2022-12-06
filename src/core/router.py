"""Core router."""
from dependencies import get_current_active_user, get_session, oauth2_scheme

from fastapi import APIRouter, Depends

from interfaces import IUser

from .report_mngr import report_mngr
from .schemas import RequestInScheme
from .schemas import RequestOutScheme
# from .exceptions import empty_request_exception
# from .schemas import ReportHeader


router = APIRouter(prefix='/report', tags=['reports'])


@router.post('/add_request_data')
async def add_request_data(data: RequestInScheme,
                           user: IUser = Depends(get_current_active_user),
                           token=Depends(oauth2_scheme),
                           session=Depends(get_session)):
    """Add products or retailers to report of current authorized user."""

    return report_mngr.add_request_data(user, data, session)


@router.delete('/remove_request_data', response_model=RequestOutScheme)
async def remove_request_data(data: RequestInScheme,
                              user: IUser = Depends(get_current_active_user),
                              token=Depends(oauth2_scheme),
                              session=Depends(get_session)):
    """Remove products or retailers from report of current authorized user."""

    return report_mngr.remove_request_data(user, data, session)









# @router.post('/add_request_data', response_model=RequestDataScheme)
# async def add_request_data(data: RequestDataScheme,
#                            user: IUser = Depends(get_current_active_user),
#                            token=Depends(oauth2_scheme)):
#     """Add products or retailers to report of current authorized user."""

#     return report_mngr.add_request_data(user, data)


# @router.delete('/remove_request_data', response_model=RequestDataScheme)
# async def remove_request_data(data: RequestDataScheme,
#                               user: IUser = Depends(get_current_active_user),
#                               token=Depends(oauth2_scheme)):
#     """Remove products or retailers from report of current authorized user."""

#     return report_mngr.remove_request_data(user, data)


# @router.post('/get_report')
# async def get_report(header: ReportHeader,
#                      user: IUser = Depends(get_current_active_user),
#                      token=Depends(oauth2_scheme),
#                      session=Depends(get_session)):
#     """
#     Start parsing process and get completed report.
#     TODO: Add response model.
#     """
#     if not bool(report_mngr.get_request(user)):
#         raise empty_request_exception
#     header.user_name = str(user)
#     return report_mngr.get_report(user, session)
