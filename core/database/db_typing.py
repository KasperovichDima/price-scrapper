"""Custom types for database module."""
from enum import Enum, auto


class UserType(Enum):
    """User typing to be saved in database."""
    USER = auto()
    ADMIN = auto()
    SUPERUSER = auto()
