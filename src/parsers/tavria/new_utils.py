"""Tavria parser utils."""
import asyncio
from functools import lru_cache
from typing import Iterable
from urllib import request

import aiohttp

from bs4 import BeautifulSoup as bs
from bs4.element import Tag

from project_typing import ElType

from . import constants as c


@lru_cache(1)
def get_product_name(tag: Tag) -> str | None:
    return tag.text.strip()\
        if 'product' in tag.get('href', '')\
        and not tag.text.isspace() else None


def group_is_outstanding(tag: Tag) -> bool:
    """Check if group has no subgroup parent."""
    try:
        return tag.parent.name == 'h4'
    except AttributeError:
        return False


def get_catalog_tags(url: str) -> Iterable[Tag]:
    """Parses home page and returns parsed tags of catalog menu."""
    response = request.urlopen(url)
    return bs(response, 'lxml').find(
        'aside', {'class': 'col-md-3 sidebar__container'}
    ).find_all()


def get_url(tag: Tag) -> str | None:
    try:
        url = tag.get('href').strip()
        assert 'catalog' in url
        return url
    except (KeyError, AssertionError, AttributeError):
        return None


def get_tag_type(tag: Tag) -> ElType | None:
    if tag.name == 'a' and 'catalog' in tag.get('href'):
        return ElType.GROUP
    elif (tag.name == 'span' and 'class' in tag.attrs
          and tag.attrs['class'][0] == 'top-sub-catalog-name')\
            or (tag.name == 'a' and tag.parent.name == 'h4'):
        return ElType.SUBCATEGORY
    elif tag.name == 'a' and tag.get('href') == '#':
        return ElType.CATEGORY
    else:
        return None


def aiohttp_session_maker() -> aiohttp.ClientSession:
    timeout = aiohttp.ClientTimeout(total=c.TAVRIA_SESSION_TIMEOUT_SEC)
    connector = aiohttp.TCPConnector(limit=c.TAVRIA_CONNECTIONS_LIMIT)
    return aiohttp.ClientSession(base_url=c.TAVRIA_URL,
                                 connector=connector,
                                 timeout=timeout)


def tasks_are_finished() -> None:
    """Just raise TimeoutError, which will be normally captured."""
    raise asyncio.exceptions.TimeoutError
