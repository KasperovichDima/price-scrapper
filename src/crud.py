"""
Database crud operations.
TODO: Add async
"""
from typing import Container, Iterable, Type

from authentication.exceptions import user_not_exists_exeption
from authentication.models import User

from catalog.models import BaseCatalogElement, Folder, Product
from catalog.schemas import FolderContent

from database import Base

from project_typing import db_type

from retailer.models import Retailer

from sqlalchemy.orm import Session


def add_instance(instance: Base, session: Session) -> None:  # type: ignore
    """Add new created instance to database."""
    session.add(instance)
    session.commit()


def add_instances(instances: Iterable[Base], session: Session) -> None:  # type: ignore  # noqa: E501
    """Add new instances to database."""
    session.add_all(instances)
    session.commit()


def get_user(email: str, session: Session) -> User | None:
    """Get user instance by email."""
    return session.query(User).filter(User.email == email).first()


async def get_folder_content(id: int, session: Session) -> FolderContent:
    """Get content of folder with specified id."""
    return FolderContent(
        products=await __get_elements(Product, session, parent_id=(id,)),
        folders=await __get_elements(Folder, session, parent_id=(id,))
    )


async def __get_elements(cls_: type[db_type], session: Session,
                         **kwargs) -> list[db_type]:
    """Returns elements of specified class using
    IN statement. NOTE: kwargs dict keys must be
    named exactly like class attributes."""

    elements = session.query(cls_)
    for k, v in kwargs.items():
        if v:
            elements = elements.filter(getattr(cls_, k).in_(v))
    return elements.all()


def get_products(session: Session, prod_ids: Container[int],
                 folder_ids: Container[int] | None = None) -> list[Product]:
    """Get product objects from product and folder ids."""

    return __get_elements(Product, session, id=prod_ids, parent_id=folder_ids)


def get_folders(session: Session,
                ids: Container[int] | None = None) -> list[Folder]:
    """
    Get folder objects by folder ids. If no
    ids are specified - all folders wil be returned.
    """
    return __get_elements(Folder, session, id=ids)


def get_retailers(ids: list[int],
                  session: Session) -> list[Retailer]:
    """Get retailer objects by retailer id."""
    return __get_elements(Retailer, session, id=ids)


def delete_user(email: str, session: Session) -> None:
    """Delete user, specified by email. Raises
    user_not_exists_exeption if email not in database."""
    if not (user := get_user(email, session)):
        raise user_not_exists_exeption
    session.delete(user)
    session.commit()
