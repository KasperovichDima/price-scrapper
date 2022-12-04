"""Report router."""
import crud

from dependencies import get_session, oauth2_scheme

from fastapi import APIRouter, Depends

from .models import get_model
from .schemas import ElementsScheme


router = APIRouter(prefix='/catalog', tags=['catalog'])


@router.get('/{cls_name}/{id}', response_model=ElementsScheme)
async def get_content(cls: str, id: int,
                      token=Depends(oauth2_scheme),
                      session=Depends(get_session)):
    """Get content of specified product catalog element."""

    model = get_model(cls)
    obj = crud.get_element(model, id, session)
    content = obj.content if obj else None
    return ElementsScheme(
        model=cls,
        content=content
    )
