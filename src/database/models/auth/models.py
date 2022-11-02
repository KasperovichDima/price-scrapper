"""Authentication models."""
from project_typing import UserType

from sqlalchemy import Boolean, Column, Enum, Integer, String

from ...config import Base


class User(Base):
    """User class."""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(20), index=True)
    last_name = Column(String(40), index=True)
    email = Column(String(100), index=True)
    is_active = Column(Boolean, default=False)
    type = Column(Enum(UserType), default=UserType.USER)

    def __repr__(self) -> str:
        return f'{self.first_name} {self.last_name}'
