"""Core custom datatypes."""
from collections import namedtuple
from typing import NamedTuple

import interfaces as i


class RequestObjects(NamedTuple):
    """Objects to be added to request."""

    folders: list[i.IFolder]
    products: list[i.IProduct]
    retailers: list[i.IRetailer]


FolderData = namedtuple('FolderData', 'grand_parent_name parent_name')
