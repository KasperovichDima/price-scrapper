"""Custom datatypes for the project."""
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


db_type = TypeVar('db_type')
