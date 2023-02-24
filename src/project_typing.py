"""Custom datatypes for the project."""
from decimal import Decimal
from typing import TypeVar

from database import Base


db_type = TypeVar('db_type', bound=Base)


PriceRecord = tuple[int, int, Decimal, Decimal | None]
