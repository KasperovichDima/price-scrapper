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

from catalog.models import Folder

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
    return (_ for _ in get_catalog(url).find_all('a')
            if 'catalog' in _.get('href'))


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


def get_catalog_folders() -> deque[tuple[str, str | None, str | None]]:
    c_name = s_name = g_name = None
    data: deque[tuple[str, str | None, str | None]] = deque()
    for tag in get_catalog(c.TAVRIA_URL).find_all():
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
        data.append((c_name, s_name, g_name))
    # removing disount
    if data[0][2] == 'Акції':
        data.popleft()
    return data


async def update_catalog(db_session: Session) -> None:
    """
    get id to folder table
    get ids of folders with childs
    collect folder ids to deprecate
    collect folder ids to undeprecate
    get map table to recognize page data with id and parent id

    get page data
    get list of folders to create
    create new folders
    invert depr/undepr
    """
    has_childs: set[int] = set()
    deprecated_ids = set()
    ids_to_deprecate: set[int] = set()
    id_to_folder: dict[int, Folder] = {}
    folders = await crud.get_folders(db_session)
    for folder in folders:
        has_childs.add(folder.parent_id)
        deprecated_ids.add(folder.id) if folder.deprecated\
            else ids_to_deprecate.add(folder.id)
        id_to_folder[folder.id] = folder

    path_to_id_parent_id: dict[tuple[str, str, str], tuple[int, int | None]] = {}
    for folder in folders:
        if not folder.parent_id:  # CATEGORY
            path = (folder.name, None, None)
            path_to_id_parent_id[path] = (folder.id, None)
            continue
        else:
            if folder.id in has_childs:  # SUBCATEGORY
                c_name = id_to_folder[folder.parent_id].name
                path = (c_name, folder.name, None)
                path_to_id_parent_id[path] = (folder.id, folder.parent_id)
                continue
            else:  # GROUP
                g_parent = None
                parent = id_to_folder[folder.parent_id]
                if parent.parent_id:  # GROUP IS IN SUBGROUP
                    g_parent = id_to_folder[parent.parent_id]
                path = (
                    g_parent.name if g_parent else parent.name,
                    parent.name if g_parent else None,
                    folder.name
                )
                path_to_id_parent_id[path] = (folder.id, folder.parent_id)

    ids_to_actualize: deque[int] = deque()
    for path in get_catalog_folders():
        if path in path_to_id_parent_id:
            path_id = path_to_id_parent_id[path][0]
            ids_to_deprecate.remove(path_id)
            if path_id in deprecated_ids:
                deprecated_ids.remove(path_id)
                ids_to_actualize.append(path_id)

        else:  # If folder is new
            match bool(path[0]), bool(path[1]), bool(path[2]):
                case _, _, True:
                    path = (path[:-1] + None)
                    path[-1] = None
