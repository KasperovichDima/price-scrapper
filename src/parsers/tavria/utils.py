"""Tavria parser utils."""
import asyncio
from collections import deque
from functools import lru_cache
from typing import Iterable
from urllib import request

import aiohttp

from bs4 import BeautifulSoup as bs
from bs4 import ResultSet
from bs4.element import Tag

from . import constants as c
from .tavria_typing import Path


def aiohttp_session_maker() -> aiohttp.ClientSession:
    timeout = aiohttp.ClientTimeout(total=c.TAVRIA_SESSION_TIMEOUT_SEC)
    connector = aiohttp.TCPConnector(limit=c.TAVRIA_CONNECTIONS_LIMIT)
    return aiohttp.ClientSession(base_url=c.TAVRIA_URL,
                                 connector=connector,
                                 timeout=timeout)


def get_catalog_urls(url: str) -> list[str]:
    """Get all catalog groups urls from specified page by url."""
    urls = [cat_url for tag in __get_group_tags(url)
            if (cat_url := __get_url(tag))]
    if 'discount' in urls[0]:
        return urls[1:]
    return urls


def __get_group_tags(url: str) -> Iterable[Tag]:
    """Returns only group tags from catalog menu."""
    return (_ for _ in __get_catalog(url).find_all('a')
            if 'catalog' in _.get('href'))


def __get_catalog(url: str) -> ResultSet[Tag]:
    """Parses home page and returns parsed tags of catalog menu."""
    response = request.urlopen(url)
    return bs(response, 'lxml').find(
        'aside', {'class': 'col-md-3 sidebar__container'}
    )


def __get_url(tag: Tag) -> str | None:
    if 'catalog' in (url := tag.get('href', '').strip()):
        return url
    return None


def tasks_are_finished() -> None:
    """Just raise TimeoutError, which will be normally captured."""
    raise asyncio.exceptions.TimeoutError


def get_page_catalog_pathes(url: str) -> deque[Path]:
    """Return path of every group in catalog.
    For example: ('beverages', 'beverages', 'beer')"""
    pathes: deque[Path] = deque()
    # category subcategory group
    c_name = s_name = g_name = None
    tag: Tag
    for tag in __get_catalog(url).find_all():
        if tag.name == 'a':
            if 'catalog' in tag.get('href'):
                g_name = tag.text.strip()
                if __group_is_outstanding(tag):
                    s_name = None
            elif tag.get('href') == '#':
                c_name = tag.text.strip()
                s_name = g_name = None
        elif __tag_is_subcat(tag):
            s_name = tag.text.strip()
            g_name = None
        else:
            continue

        pathes.append((c_name, s_name, g_name))

    return __remove_discount(pathes)


def __group_is_outstanding(tag: Tag) -> bool:
    """Check if group has no subgroup parent."""
    try:
        return tag.parent.name == 'h4'
    except AttributeError:
        return False


def __tag_is_subcat(tag: Tag) -> bool:
    return (tag.name == 'span'
            and tag.attrs.get('class') == ['top-sub-catalog-name'])


def __remove_discount(pathes: deque[Path]) -> deque[Path]:
    """Remove 'discount' path if it is first in pathes."""
    if pathes[0][2] == 'Акції':
        pathes.popleft()
    assert pathes[0][0]
    return pathes


@lru_cache(maxsize=1)
def cut_path(path: Path) -> Path:  # type: ignore
    """
    Cut given path to get parent path. Attempt
    to cut path of category is not allowed.
    >>> cut_path('Cat_name', 'Sub_name', 'Group_name')
    ('Cat_name', 'Sub_name', None)
    >>> cut_path('Cat_name', None, 'Group_name')
    ('Cat_name', None, None)
    """
    assert any((path[1], path[2]))

    for i in range(1, len(path) + 1):
        if path[-i]:
            return path[:-i] + (None,) * i  # type: ignore


def get_folder_name(path: Path) -> str:
    """
    Returns last specified name in the path.
    >>> get_folder_name('Cat_name', 'Sub_name', 'Group_name')
    'Group_name'
    >>> get_folder_name('Cat_name', 'Sub_name', None)
    'Sub_name'
    """
    for name in path[::-1]:
        if name:
            return name
    raise ValueError('All names are empty.')
