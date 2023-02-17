"""Authentication models."""
from database import Base

from exceptions import EqCompareError

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column  # type: ignore

from .auth_typing import UserType


class User(Base):
    """System user representation."""

    __tablename__ = 'user'

    first_name: Mapped[str] = mapped_column(String(20), index=True)
    last_name: Mapped[str] = mapped_column(String(40), index=True)
    email: Mapped[str] = mapped_column(String(100), index=True)
    password: Mapped[str] = mapped_column(String(250))
    is_active: Mapped[bool] = mapped_column(default=False)
    type: Mapped[UserType] = mapped_column(default=UserType.USER)

    def __repr__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def __hash__(self) -> int:
        return hash(self.email)

    def __eq__(self, __o: object) -> bool:
        try:
            return self.email == __o.email  # type: ignore
        except AttributeError:
            raise EqCompareError(self, __o)
