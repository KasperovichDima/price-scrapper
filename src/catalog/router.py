"""Report router."""
import crud

from dependencies import get_session, oauth2_scheme

from fastapi import APIRouter, Depends

from project_typing import CatalogModels

from .models import get_model


router = APIRouter(prefix='/catalog', tags=['catalog'])


@router.get('/{cls_name}/{id}', response_class=)
async def get_content(cls: CatalogModels, id: int,
                      token=Depends(oauth2_scheme),
                      session=Depends(get_session)):
    """Get content of specified product catalog element."""

    model = get_model(cls)
    obj = crud.get_element(model, id, session)
    return obj.content if obj else None
