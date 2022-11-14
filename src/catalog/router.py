"""Report router."""
from dependencies import oauth2_scheme

from fastapi import APIRouter, Depends


router = APIRouter(prefix='/catalog', tags=['catalog'])


@router.get('/{cls_name}/{id}')
def get_content(cls_name: str, id: int, token=Depends(oauth2_scheme)):
    """Get content of product catalog specified element."""
