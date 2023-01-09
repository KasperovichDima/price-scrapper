"""Authentication models."""
from base_models import BaseWithID

from project_typing import UserType

from sqlalchemy import Boolean, Column, Enum, String


class User(BaseWithID):
    """System user representation."""

    __tablename__ = 'user'

    first_name = Column(String(20), index=True)
    last_name = Column(String(40), index=True)
    email = Column(String(100), index=True)
    password = Column(String(250))
    is_active = Column(Boolean, default=False)
    type = Column(Enum(UserType), default=UserType.USER)

    def __repr__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def __hash__(self) -> int:
        return hash(self.email)

    def __eq__(self, __o: object) -> bool:
        return self.email == __o.email
