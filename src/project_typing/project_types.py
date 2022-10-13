"""Custom datatypes, required for project."""
from enum import Enum, auto


class ShopName(Enum):
    """Enum to shop choosing."""
    TAVRIA = 'TAVRIA V'
    SILPO = 'SILPO'
    KOPEIKA = 'KOPEIKA'
    EPICENTR = 'EPICENTR'


class UserType(Enum):
    """Enum user type to be saved in database."""
    USER = auto()
    ADMIN = auto()
    SUPERUSER = auto()


class ElNames(Enum):
    """Enum catalog element name."""
    CATEGORY = 'Category'
    SUBCATEGORY = 'SubCategory'
    GROUP = 'Group'
    SUBGROUP = 'SubGroup'
    PRODUCT = 'Product'
