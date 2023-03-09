"""Custom datatypes for the project."""
from decimal import Decimal
from typing import TypeAlias, TypeVar

from database import Base


db_type = TypeVar('db_type', bound=Base)


PriceTuple: TypeAlias = tuple[int, int, Decimal, Decimal | None]

NameRetailPromo: TypeAlias = tuple[str, Decimal, Decimal | None]
