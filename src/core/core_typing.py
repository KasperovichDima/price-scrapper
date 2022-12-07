"""Core custom datatypes."""
from typing import NamedTuple

import interfaces as i


class RequestObjects(NamedTuple):
    """Objects to be added to request."""

    folders: list[i.IFolder]
    products: list[i.IProduct]
    retailers: list[i.IRetailer]
