"""Base parsing strategy."""
from collections import deque
from typing import Any

import interfaces as i


class BaseStrategy(i.IParserStrategy):
    """Base strategy class."""

    def __call__(self, prod_by_url: dict[str, deque[i.IProduct]]) -> Any:
        """"""

        
