"""Report router."""
import crud

from dependencies import get_session, oauth2_scheme

from fastapi import APIRouter, Depends

from .schemas import FolderContent


router = APIRouter(prefix='/catalog', tags=['catalog'])


@router.get('/folder_content/{id}', response_model=FolderContent)
async def folder_content(id: int, token=Depends(oauth2_scheme),
                         session=Depends(get_session)):
    """Get content of folder with specified id."""

    return crud.get_folder_content(id, session)
