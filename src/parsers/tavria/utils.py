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

import crud

from project_typing import ElType

from sqlalchemy.orm import Session

from . import constants as c
from .tavria_typing import Parents, Path


def group_is_outstanding(tag: Tag) -> bool:
    """Check if group has no subgroup parent."""
    try:
        return tag.parent.name == 'h4'
    except AttributeError:
        return False


def get_catalog(url: str) -> ResultSet[Tag]:
    """Parses home page and returns parsed tags of catalog menu."""
    response = request.urlopen(url)
    return bs(response, 'lxml').find(
        'aside', {'class': 'col-md-3 sidebar__container'}
    )


def get_group_tags(url: str) -> Iterable[Tag]:
    """Returns only group tags from catalog menu."""
    return (_ for _ in get_catalog(url).find_all('a')
            if 'catalog' in _.get('href'))


def get_url(tag: Tag) -> str | None:
    if 'catalog' in (url := tag.get('href', '').strip()):
        return url
    return None


def __get_type_checker():
    """TODO: Could be unsafe if call it one more time!"""
    discount_checked = False

    def get_tag_type(tag: Tag) -> ElType | None:
        if tag.name == 'a' and 'catalog' in tag.get('href'):
            nonlocal discount_checked
            if not discount_checked:
                if 'discount' in tag.get('href'):
                    discount_checked = True
                    return None
            return ElType.GROUP
        elif (tag.name == 'span' and 'class' in tag.attrs
              and tag.attrs['class'][0] == 'top-sub-catalog-name')\
                or (tag.name == 'a' and tag.parent.name == 'h4'):
            return ElType.SUBCATEGORY
        elif tag.name == 'a' and tag.get('href') == '#':
            return ElType.CATEGORY
        else:
            return None
    return get_tag_type


tag_type_for = __get_type_checker()


def aiohttp_session_maker() -> aiohttp.ClientSession:
    timeout = aiohttp.ClientTimeout(total=c.TAVRIA_SESSION_TIMEOUT_SEC)
    connector = aiohttp.TCPConnector(limit=c.TAVRIA_CONNECTIONS_LIMIT)
    return aiohttp.ClientSession(base_url=c.TAVRIA_URL,
                                 connector=connector,
                                 timeout=timeout)


def tasks_are_finished() -> None:
    """Just raise TimeoutError, which will be normally captured."""
    raise asyncio.exceptions.TimeoutError


async def get_groups_parent_to_id(db_session: Session) -> dict[Parents, int]:
    folders = await crud.get_folders(db_session)
    id_to_folder = {_.id: _ for _ in folders}
    parents_to_id: dict[Parents, int] = {}
    for group in (_ for _ in folders if _.el_type is ElType.GROUP):
        p_folder = id_to_folder[group.parent_id]
        gp_folder = id_to_folder.get(p_folder.parent_id)
        c_name = gp_folder.name if gp_folder else p_folder.name
        s_name = p_folder.name if gp_folder else None
        g_name = group.name
        parents = (c_name, s_name, g_name)
        parents_to_id[parents] = group.id
    return parents_to_id


def get_page_catalog_pathes(url: str) -> deque[Path]:
    s_name = g_name = None
    pathes: deque[tuple[str, str | None, str | None]] = deque()
    for tag in get_catalog(url).find_all():
        match tag_type_for(tag):
            case ElType.GROUP:
                g_name = tag.text.strip()
                if group_is_outstanding(tag):
                    s_name = None
            case ElType.SUBCATEGORY:
                s_name = tag.text.strip()
                g_name = None
            case ElType.CATEGORY:
                c_name = tag.text.strip()
                s_name = g_name = None
            case _:
                continue
        assert c_name
        pathes.append((c_name, s_name, g_name))
    return remove_discount(pathes)


def remove_discount(pathes: deque[Path]) -> deque[Path]:
    """Remove 'discount' path if it is first in pathes."""
    if pathes[0][2] == 'Акції':
        pathes.popleft()
    return pathes


@lru_cache(maxsize=1)
def cut_path(path: Path) -> Path:  # type: ignore
    """
    Cut passed path to get parent path. Attempt
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
