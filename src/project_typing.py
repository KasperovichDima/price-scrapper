"""Custom datatypes for the project."""
from decimal import Decimal
from typing import TypeVar


db_type = TypeVar('db_type')


PriceRecord = tuple[int, int, Decimal, Decimal | None]
