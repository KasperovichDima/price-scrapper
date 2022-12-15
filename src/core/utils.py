"""Core utilites."""
import crud

from sqlalchemy.orm import Session

from .core_typing import RequestObjects
from .schemas import RequestInScheme


def get_request_objects(in_data: RequestInScheme,
                        session: Session) -> RequestObjects:
    """Get objects for request by specified ids."""
    return RequestObjects(
        crud.get_folders(session, ids=in_data.folders),
        crud.get_products(session, in_data.products),
        crud.get_retailers(in_data.retailers, session),
    )
