"""Catalog router."""
import crud

from dependencies import get_db_session, oauth2_scheme

from fastapi import APIRouter, Depends, Path

from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import FolderContent


router = APIRouter(prefix='/catalog', tags=['catalog'])


@router.get('/folder_content/{id}', response_model=FolderContent)
async def get_folder_content(id: int = Path(gt=0),
                             session=Depends(get_db_session),
                             token=Depends(oauth2_scheme)):
    """Get content of folder with specified id. It
    could be folders, products or folders and products."""

    return await crud.get_folder_content(id, session)


@router.delete('/delete_folder/{id}')
async def delete_folder(id: int = Path(gt=0),
                        session: AsyncSession = Depends(get_db_session),
                        token=Depends(oauth2_scheme)) -> int:
    """Delete folder and all folder's content. Folder to
    delete is specified by id. Returns deleted folder id."""
    deleted_id = await crud.delete_folder(id, session)
    await session.commit()
    return deleted_id
