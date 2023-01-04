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

from project_typing import ElType

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


def get_folder_content(id: int, session: Session) -> FolderContent:
    """Get content of folder with specified id."""
    return FolderContent(
        products=session.query(Product).filter(Product.parent_id == id).all(),
        folders=session.query(Folder).filter(Folder.parent_id == id).all()
    )


def get_element(cls: Type[BaseCatalogElement], id: int,
                session: Session) -> BaseCatalogElement | None:
    """Returns catalog instance with specified params, if exists."""
    return session.get(cls, id)


def get_products(session: Session, prod_ids: Container[int],
                 folder_ids: Container[int] | None = None) -> list[Product]:
    """Get product objects from product and folder ids."""
    return session.query(Product).where(
            Product.id.in_(prod_ids)
            | Product.parent_id.in_(folder_ids if folder_ids else [])
        ).all()


def get_folders(session: Session,
                ids: Container[int] | None = None) -> list[Folder]:
    """
    Get folder objects by folder ids. If no
    ids are specified - all folders wil be returned.
    TODO: Try to refactor after migration to postgres.
    """

    folders = session.query(Folder)
    if ids:
        folders = folders.where(Folder.id.in_(ids))
    return folders.all()


def get_retailers(ids: list[int],
                  session: Session) -> list[Retailer]:
    """Get retailer objects by retailer names."""
    return session.query(Retailer).where(Retailer.id.in_(ids)).all()


def delete_user(email: str, session: Session) -> None:
    """Delete user, specified by email. Raises
    user_not_exists_exeption if email not in database."""
    if not (user := get_user(email, session)):
        raise user_not_exists_exeption
    session.delete(user)
    session.commit()
