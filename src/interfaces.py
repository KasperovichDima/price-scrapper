"""
Project Interfaces.
TODO: Move all docstrings here.
"""
from __future__ import annotations

from abc import ABC


class IBaseWithID(ABC):
    """Base interface, containing id: int."""

    id: int


class IUser(IBaseWithID):
    """User interface."""


class IElement(IBaseWithID):
    """Catalog element interface."""

    name: str


class IFolder(IElement):
    """Folder interface."""


class IProduct(IElement):
    """Product intrface."""


class IRetailer(IBaseWithID):
    """Retailer interface."""

    name: str
