"""Database crud operations."""
from authentication.models import User

from database import Base

from sqlalchemy.orm import Session


def get_user(email: str, db: Session) -> User | None:
    """Get user instance by email."""
    return db.query(User).filter(User.email == email).first()


def add_instance(instance: Base, db: Session):
    """Add new created instance to database."""
    db.add(instance)
    db.commit()
