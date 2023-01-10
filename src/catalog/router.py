"""Catalog router."""
import crud

from dependencies import get_session, oauth2_scheme

from fastapi import APIRouter, Depends

from .schemas import FolderContent


router = APIRouter(prefix='/catalog', tags=['catalog'])


@router.get('/folder_content/{id}', response_model=FolderContent)
async def get_folder_content(id: int, token=Depends(oauth2_scheme),
                             session=Depends(get_session)):
    """Get content of folder with specified id."""

    return await crud.get_folder_content(id, session)


@router.delete('/delete_folder/{id}')
async def delete_folder(id: int, session=Depends(get_session),
                        token=Depends(oauth2_scheme)) -> int:
    """Delete folder, specified by id."""
    return await crud.try_to_delete_folder(id, session)
