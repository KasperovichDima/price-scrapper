"""Tag data collector."""
from collections import defaultdict, deque
from typing import Iterable

from bs4.element import Tag

from project_typing import ElType

from .utils import get_catalog_tags
from .utils import get_type
from .utils import tag_is_interesting
from .utils import get_url
from ...schemas import CatalogFactory


class FactoryCreator:
    """
    Makes request to source url.
    Parses tags, extracts data.
    Prapares data for objects creation.
    """
    __tags: Iterable[Tag]
    __current_tag: Tag
    __current_names = dict.fromkeys(ElType)
    __current_factories: dict[ElType, CatalogFactory] = {}
    __factories: defaultdict[ElType, deque[CatalogFactory]]\
        = defaultdict(deque)

    def __init__(self ,home_url: str) -> None:
        type_ = ElType.CATEGORY
        cat_factory = CatalogFactory(obj_type=type_)
        self.__factories[type_].append(cat_factory)
        self.__current_factories[type_] = cat_factory

    def __call__(self,
                 ) -> defaultdict[ElType, deque[CatalogFactory]]:
        self.__tags = get_catalog_tags(home_url)
        self.__create_factories()
        return self.__factories