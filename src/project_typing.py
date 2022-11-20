"""Custom datatypes for the project."""
from enum import Enum, auto


class UserType(Enum):
    """Enum user type to be saved in database."""

    USER = auto()
    ADMIN = auto()
    SUPERUSER = auto()


class Retailers(Enum):
    """Enum of retailer names."""

    EPICENTR = 'Epicentr'
    SANTIM = 'Santim'
    SILPO = 'Silpo'
    TAVRIA = 'Tavria V'


cat_elements = dict[str, list[int]]
