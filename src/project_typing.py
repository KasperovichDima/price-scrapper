"""Custom datatypes for the project."""
from __future__ import annotations

from decimal import Decimal
from enum import Enum, auto
from typing import TypeVar


class UserType(Enum):
    """Enum user type to be saved in database."""

    USER = auto()
    ADMIN = auto()
    SUPERUSER = auto()


db_type = TypeVar('db_type')


PriceRecord = tuple[int, int, Decimal, Decimal | None]
