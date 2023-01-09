"""Database crud operations."""
from typing import Iterable, Sequence

from authentication.exceptions import user_not_exists_exeption
from authentication.models import User

from base_models import BaseWithID

from catalog.models import Folder, Product
from catalog.schemas import FolderContent

from project_typing import db_type

from retailer.models import Retailer

from sqlalchemy import delete
from sqlalchemy.orm import Session


async def add_instance(instance: BaseWithID, session: Session) -> None:
    """Add new instance to database."""
    session.add(instance)
    session.commit()


async def add_instances(instances: Iterable[BaseWithID],
                        session: Session) -> None:
    """Add new instances to database."""
    session.add_all(instances)
    session.commit()


async def get_user(email: str, session: Session) -> User | None:
    """Get user instance by email."""
    return session.query(User).filter(User.email == email).first()


async def get_folder_content(id: int, session: Session) -> FolderContent:
    """Get content of folder with specified id."""
    return FolderContent(
        products=await __get_elements(Product, session, parent_id=(id,)),
        folders=await __get_elements(Folder, session, parent_id=(id,))
    )


async def __get_elements(cls_: type[db_type], session: Session,
                         **params) -> list[db_type]:
    """Returns elements of specified class using
    IN statement. NOTE: kwargs dict keys must be
    named exactly like class attributes."""

    elements = session.query(cls_)
    for param_name, seq in params.items():
        if seq:
            elements = elements.filter(getattr(cls_, param_name).in_(seq))
    return elements.all()


async def get_products(
    session: Session,
    prod_ids: Iterable[int],
    folder_ids: Iterable[int] | None = None
) -> list[Product]:
    """Get product objects from product and folder ids."""

    return await __get_elements(Product, session, id=prod_ids,
                                parent_id=folder_ids)


async def get_folders(session: Session,
                      ids: Iterable[int] | None = None) -> list[Folder]:
    """
    Get folder objects by folder ids. If no
    ids are specified - all folders wil be returned.
    """
    return await __get_elements(Folder, session, id=ids)


async def get_retailers(ids: list[int],
                        session: Session) -> list[Retailer]:
    """Get retailer objects by retailer id."""
    return await __get_elements(Retailer, session, id=ids)


async def delete_cls_instances(instances: Sequence[BaseWithID],
                               session: Session) -> None:
    """
    Remove specified objects from database.
    NOTE: All objects must the same class.
    Raises assertion error if not.
    """
    cls_ = instances[0].__class__
    assert all((isinstance(_, cls_) for _ in instances))
    session.execute(delete(cls_).where(cls_.id.in_((_.id for _ in instances))))
    session.commit()


async def delete_user(email: str, session: Session) -> None:
    """Delete user, specified by email. Raises
    user_not_exists_exeption if email not in database."""
    if not (user := await get_user(email, session)):
        raise user_not_exists_exeption
    session.delete(user)
    session.commit()
