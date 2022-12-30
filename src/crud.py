"""
Database crud operations.
TODO: Add async
"""
from typing import Iterable, Type

from authentication.models import User

from catalog.models import BaseCatalogElement, Folder, Product
from catalog.schemas import FolderContent

from database import Base

from project_typing import ElType

from retailer.models import Retailer

from sqlalchemy.orm import Session


def get_user(email: str, session: Session) -> User | None:
    """Get user instance by email."""
    return session.query(User).filter(User.email == email).first()


def delete_user(user: User, session: Session) -> None:
    """Delete specified user."""
    session.delete(user)
    session.commit()


def add_instance(instance: Base, session: Session) -> None:  # type: ignore
    """Add new created instance to database."""
    session.add(instance)
    session.commit()


def add_instances(instances: Iterable[Base], session: Session) -> None:  # type: ignore  # noqa: E501
    """Add new instances to database."""
    session.add_all(instances)
    session.commit()


def get_element(cls: Type[BaseCatalogElement], id: int,
                session: Session) -> BaseCatalogElement | None:
    """Returns catalog instance with specified params, if exists."""
    return session.get(cls, id)


def get_folder_content(id: int, session: Session) -> FolderContent:
    """Get content of folder with specified id."""
    return FolderContent(
        products=session.query(Product).filter(Product.parent_id == id).all(),
        folders=session.query(Folder).filter(Folder.parent_id == id).all()
    )


def get_products(session: Session, prod_ids: list[int],
                 folder_ids: list[int] | None = None) -> list[Product]:
    """Get product objects from product and folder ids."""
    return session.query(Product).where(
            Product.id.in_(prod_ids) |
            Product.parent_id.in_(folder_ids if folder_ids else [])
        ).all()


def get_folders(session: Session, /,
                ids: Iterable[int] = [],
                names: Iterable[str] = [],
                types: Iterable[ElType] = []) -> list[Folder]:
    """
    Get folder objects by folder ids or(and) folder names. If no
    ids or names are specified - all folders wil be returned.
    TODO: Try to refactor after migration.
    """
    folders = session.query(Folder)
    if ids:
        folders = folders.where(Folder.id.in_(ids))
    if names:
        folders = folders.where(Folder.name.in_(names))
    if types:
        folders = folders.where(Folder.el_type.in_(types))

    return folders.all()


def get_retailers(ids: list[int],
                  session: Session) -> list[Retailer]:
    """Get retailer objects by retailer names."""
    return session.query(Retailer).where(Retailer.id.in_(ids)).all()
