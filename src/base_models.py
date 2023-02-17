"""Base models for inheritance."""
from database.config import Base


class BaseWithRepr(Base):
    """Base model class for classes with str 'name' field.
    Implements all BaseWithID features + __repr__."""

    __abstract__ = True

    def __repr__(self) -> str:
        return self.name
