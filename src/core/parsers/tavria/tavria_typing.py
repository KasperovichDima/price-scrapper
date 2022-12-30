"""Tavria parser typing."""
from collections import namedtuple
from typing import Generator

from catalog.models import BaseCatalogElement


ObjectParents = namedtuple('ObjectParents', 'grand_parent_name parent_name')
BaseFactoryReturnType = Generator[BaseCatalogElement, None, None]
