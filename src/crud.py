"""
CRUD database functions.
TODO: Complete refactoring.
"""
from typing import Iterable, List, Optional, Type
from sqlalchemy.orm import Session

import interfaces as i
from models import get_model_by_name
from project_typing import ElNames


def get_content_by_model(model: Type[i.ICatalogElement],
    id: int, db_session: Session) -> Iterable[i.ICatalogElement]:
    """Get inline contentof some catalog element."""
    element: i.ICatalogElement = db_session.query(model).filter(model.id==id).first()
    return element.content

def get_elements(model: Type[i.ICatalogElement], db_session: Session) -> List[i.ICatalogElement]:
    """Get all content of specified model."""
    return db_session.query(model).all()

def get_element(model: i.ICatalogElement, el_id: int,
    db_session: Session) -> Optional[i.ICatalogElement]:
    """Get one element of specified model dbselected by id."""
    return db_session.query(model).filter(id=el_id)

def get_content_by_model_name(name: ElNames, id: int,
    db_session: Session) -> Iterable[i.ICatalogElement]:
    """Get inline content by specified model name and specified id."""
    if name == 'root':
        model = get_model_by_name(ElNames.CATEGORY)
        return get_elements(model, db_session)
    model = get_model_by_name(name)
    return get_content_by_model(model, id, db_session)
