"""Database crud operations."""
from typing import Iterable, Type

from authentication.models import User

from catalog.models import Folder, Product
from catalog.schemas import FolderContent

from database import Base

import interfaces as i
from project_typing import ElType

from retailer.models import Retailer

from sqlalchemy import and_, or_
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


def get_element(cls: Type[i.ICatalogElement], id: int,
                session: Session) -> i.ICatalogElement | None:
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
        or_(
            Product.id.in_(prod_ids),  # type: ignore
            Product.parent_id.in_(folder_ids if folder_ids else [])
            )
        ).all()


def get_folders(session: Session,
                ids: Iterable[int] = (),
                names: Iterable[str] = (),
                type_: ElType | None = None) -> list[Folder]:
    """
    Get folder objects by folder ids or(and) folder names. If no
    ids or names are specified - all folders wil be returned.
    """
    folders = session.query(Folder)
    if ids or names:
        folders = folders.where(
        and_(
            Folder.id.in_(ids),
            Folder.name.in_(names)),  # type: ignore
            Folder.type == type_
        )
    return folders.all()


def get_retailers(ids: list[int],
                  session: Session) -> list[Retailer]:
    """Get retailer objects by retailer names."""
    return session.query(Retailer).where(Retailer.id.in_(ids)).all()
