"""Custom datatypes for the project."""
from __future__ import annotations

from enum import Enum, auto
from typing import TypeVar


class UserType(Enum):
    """Enum user type to be saved in database."""

    USER = auto()
    ADMIN = auto()
    SUPERUSER = auto()


class ElType(Enum):
    """Levels of catalog folders. NOTE: Order matters! Do not change!"""

    CATEGORY = auto()
    SUBCATEGORY = auto()
    GROUP = auto()
    PRODUCT = auto()


folder_types = [_ for _ in ElType if _ is not ElType.PRODUCT]


db_type = TypeVar('db_type')


PriceRecord = tuple[int, int, float, float | None]
