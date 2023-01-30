"""Custom datatypes for tavria parser."""
from collections import defaultdict, deque

from project_typing import ElType

from .factory import BaseFactory


Factories = defaultdict[ElType, deque[BaseFactory]]
