"""Core custom datatypes."""
from collections import deque
from typing import Iterable, NamedTuple

import interfaces as i

from sqlalchemy.orm import Session


ProductsByURL = dict[str, deque[i.IProduct]]


class ParserData(NamedTuple):
    """Contains all data, required for parsing process"""

    header_id: int
    products_by_url: ProductsByURL
    retailers: Iterable[i.IRetailer]
    session: Session
