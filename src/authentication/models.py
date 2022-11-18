"""Authentication models."""
from database.config import Base

from interfaces import IUser

from project_typing import UserType

from sqlalchemy import Boolean, Column, Enum, Integer, String
from sqlalchemy.orm import relationship


class User(Base, IUser):
    """System user representation."""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(20), index=True)
    last_name = Column(String(40), index=True)
    email = Column(String(100), index=True)
    password = Column(String(250))
    is_active = Column(Boolean, default=False)
    type = Column(Enum(UserType), default=UserType.USER)

    headers = relationship('ReportHeader', back_populates='user')

    def __repr__(self) -> str:
        return f'{self.first_name} {self.last_name}'
