"""Database crud operations."""
from typing import Iterable, Type

from authentication.models import User

from database import Base

from interfaces import IElement

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


def get_element(cls: Type[IElement], id: int,
                session: Session) -> IElement | None:
    """Returns catalog instance with specified params, if exists."""
    return session.get(cls, id)
