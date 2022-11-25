"""Core custom datatypes."""
from collections import deque

import interfaces as i


ProductsByURL = dict[str, deque[i.IProduct]]
