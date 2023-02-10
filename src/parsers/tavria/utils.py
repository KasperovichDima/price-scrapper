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

from parsers import schemas as s

from project_typing import ElType

from pydantic import BaseModel

from sqlalchemy.orm import Session

from . import constants as c
from .tavria_typing import Parents


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


def get_catalog(url: str) -> ResultSet[Tag]:
    """Parses home page and returns parsed tags of catalog menu."""
    response = request.urlopen(url)
    return bs(response, 'lxml').find(
        'aside', {'class': 'col-md-3 sidebar__container'}
    )


def get_group_tags(url: str) -> Iterable[Tag]:
    """Returns only group tags from catalog menu."""
    return (_ for _ in get_catalog(url).find_all('a') if 'catalog' in _.get('href'))


def get_url(tag: Tag) -> str | None:
    if 'catalog' in (url := tag.get('href', '').strip()):
        return url
    return None


def get_type_checker():
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


tag_type_for = get_type_checker()


def aiohttp_session_maker() -> aiohttp.ClientSession:
    timeout = aiohttp.ClientTimeout(total=c.TAVRIA_SESSION_TIMEOUT_SEC)
    connector = aiohttp.TCPConnector(limit=c.TAVRIA_CONNECTIONS_LIMIT)
    return aiohttp.ClientSession(base_url=c.TAVRIA_URL,
                                 connector=connector,
                                 timeout=timeout)


def tasks_are_finished() -> None:
    """Just raise TimeoutError, which will be normally captured."""
    raise asyncio.exceptions.TimeoutError


def create_schema_getter():
    schemas = {
        ElType.CATEGORY: s.CategoryFactoryIn,
        ElType.SUBCATEGORY: s.SubCategoryFactoryIn,
        ElType.GROUP: s.GroupFactoryIn,
        ElType.PRODUCT: s.ProductFactoryIn
    }

    def get_schema(type_: ElType) -> type[BaseModel]:
        return schemas[type_]
    return get_schema


get_schema_for = create_schema_getter()


def factories_are_valid(factories) -> bool:
    return len(factories[ElType.GROUP])\
        == len(set(factories[ElType.GROUP]))


async def get_parent_id_table(db_session: Session) -> dict[Parents, int]:
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
