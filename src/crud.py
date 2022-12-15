"""Database crud operations."""
from typing import Iterable, Type

from authentication.models import User

from catalog.models import Folder, Product
from catalog.schemas import FolderContent

from database import Base

import interfaces as i

from retailer.models import Retailer

from sqlalchemy import or_
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


# def del_instances(instances: Iterable[Base], session: Session) -> None:
#     """Delete instances from database."""
#         session.

def get_element(cls: Type[i.IElement], id: int,
                session: Session) -> i.IElement | None:
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


# def get_folders(ids: list[int], session: Session) -> list[Folder]:
#     """Get folder bjects by folder ids."""
#     return session.query(Folder).where(Folder.id.in_(ids)).all()

def get_folders(session: Session, ids: Iterable[int] | None = None,
                names: Iterable[int] | None = None) -> list[Folder]:
    """
    Get folder bjects by folder ids or(and) folder names
    (optional). ids OR(AND) names MUST be specified.
    """
    if not (ids or names):
        raise ValueError('ids OR(AND) names are required, NOT None of them.')
    return session.query(Folder).where(
        or_(
            Folder.id.in_(ids if ids else []),
            Folder.name.in_(names if names else []))  # type: ignore
        ).all()


def get_retailers(ids: list[int],
                  session: Session) -> list[Retailer]:
    """Get retailer objects by retailer names."""
    return session.query(Retailer).where(Retailer.id.in_(ids)).all()


# def get_products(element_ids: defaultdict[str, set[int]],
#                  session: Session) -> list[Product]:
#     """
#     Get products by request el_names.
#     TODO: This method should be added when other container
#           catalog instances will be created.
#     """

#     return session.query(Product).where(
#         or_(
#             Product.id.in_(element_ids['Product']),  # type: ignore
#             Product.subgroup_id.in_(element_ids['Subgroup'])
#             )
#         ).all()
