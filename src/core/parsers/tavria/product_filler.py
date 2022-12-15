"""Tavria product filler."""
from .utils import get_catalog_tags


class ProductFiller:
    """Fill catalog tree with products. Also used for detecting new products."""

    def __init__(self, home_url: str) -> None:
        self.__cat_tags = get_catalog_tags(home_url)
        