"""Custom datatypes for the project."""
from enum import Enum, auto


class UserType(Enum):
    """Enum user type to be saved in database."""
    USER = auto()
    ADMIN = auto()
    SUPERUSER = auto()