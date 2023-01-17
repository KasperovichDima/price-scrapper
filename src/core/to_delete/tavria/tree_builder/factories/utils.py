"""get_factory_class function."""
from functools import lru_cache

from bs4.element import Tag


@lru_cache(1)
def get_product_name(tag: Tag) -> str | None:
    return tag.text.strip()\
        if 'product' in tag.get('href', '')\
        and not tag.text.isspace() else None
