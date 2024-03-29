"""Core utilites."""
import crud

from sqlalchemy.ext.asyncio import AsyncSession

from .core_typing import RequestObjects
from .schemas import RequestInScheme


async def get_request_objects(in_data: RequestInScheme,
                              session: AsyncSession) -> RequestObjects:
    """Get objects for request by specified ids."""
    return RequestObjects(
        await crud.get_folders(session, ids=in_data.folders),
        await crud.get_products(session, in_data.products),
        await crud.get_retailers(in_data.retailers, session),
    )
