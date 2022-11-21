"""Database crud operations."""
from typing import Container, Iterable, Type

from authentication.models import User

from database import Base
from database import Retailer

import interfaces as i

from sqlalchemy.orm import Session


def get_user(email: str, session: Session) -> User | None:
    """Get user instance by email."""
    return session.query(User).filter(User.email == email).first()


def delete_user(user: User, session: Session) -> None:
    """Delete specified user."""
    session.delete(user)
    session.commit()


def add_instance(instance: Base, session: Session) -> None:
    """Add new created instance to database."""
    session.add(instance)
    session.commit()


def add_instances(instances: Iterable[Base], session: Session) -> None:
    """Add new created instance to database."""
    session.add_all(instances)
    session.commit()


def get_element(cls: Type[i.IElement], id: int,
                session: Session) -> i.IElement | None:
    """Returns catalog instance with specified params, if exists."""
    return session.get(cls, id)


def get_retailers(retailers: Container[str],
                  session: Session) -> Iterable[i.IRetailer]:
    """Get retailer objects by retailer names."""

    return session.query(Retailer).filter(Retailer.name.in_(retailers)).all()
