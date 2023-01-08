"""Base models for inheritance."""
from database.config import Base

from sqlalchemy import Column, Integer


class BaseWithID(Base):  # type: ignore
    """Base model class with int id as primary key + __hash__ and __eq__."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)

    def __eq__(self, __o: object) -> bool:
        return hash(self) == hash(__o)

    def __hash__(self) -> int:
        return hash(self.id)


class BaseWithRepr(BaseWithID):
    """Base model class for classes with str 'name' field.
    Implements all BaseWithID features + __repr__."""

    __abstract__ = True

    def __repr__(self) -> str:
        return self.name
