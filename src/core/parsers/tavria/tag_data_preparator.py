"""Tag data collector."""
from collections import defaultdict, deque
from typing import Iterable

from bs4.element import Tag

from project_typing import ElType
from pydantic import ValidationError

from .factories import CatalogFactory
from .factories import get_factory_class
from .utils import get_catalog_tags
from .utils import get_type
from .utils import tag_is_interesting
from .utils import get_url


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

    def __init__(self, home_url: str) -> None:
        self.__tags = get_catalog_tags(home_url)
        type_ = ElType.CATEGORY
        cat_factory = CatalogFactory(obj_type=type_)
        self.__factories[type_].append(cat_factory)
        self.__current_factories[type_] = cat_factory

    def __call__(self) -> defaultdict[ElType, deque[CatalogFactory]]:
        self.__create_factories()
        return self.__factories

    def __create_factories(self) -> None:
        """Prepare catalog factories from site information."""

        for tag in self.__tags:
            try:
                assert tag_is_interesting(tag)
                self.__current_tag = tag
                self.__process_tag()
            except (AssertionError, KeyError, TypeError):
                pass

    def __process_tag(self) -> None:
        type_ = get_type(self.__current_tag)
        self.__change_current_name(type_)

        if type_ is ElType.CATEGORY:
            self.__recreate_factory(ElType.SUBCATEGORY)

        elif type_ is ElType.SUBCATEGORY:
            self.__recreate_factory(ElType.GROUP)

        elif type_ is ElType.GROUP:
            if self.__current_tag.parent.name == 'h4':
                self.__current_names[ElType.SUBCATEGORY] = None
                self.__recreate_factory(ElType.GROUP)
            self.__recreate_factory(ElType.PRODUCT)

        self.__current_factories[type_]\
            .add_name(self.__current_tag.text.strip())

    def __change_current_name(self, type_: ElType) -> None:
        self.__current_names[type_] = self.__current_tag.text.strip()

    def __recreate_factory(self, type_: ElType) -> None:
        self.__try_to_close_factory(type_)
        self.__try_to_create_factory(type_)

    def __try_to_close_factory(self, type_: ElType) -> None:
        try:
            assert self.__factory_is_ready_to_close(type_)
            self.__close_factory(type_)
        except (AssertionError, KeyError):
            pass

    def __factory_is_ready_to_close(self, type_: ElType) -> bool:
        return type_ in self.__current_factories\
            or (type_ is not ElType.PRODUCT
                and bool(self.__current_factories[type_]))

    def __close_factory(self, type_: ElType) -> None:
        self.__factories[type_].append(self.__current_factories.pop(type_))

    def __try_to_create_factory(self, type_: ElType):
        try:
            self.__create_factory(type_)
        except ValidationError:
            pass

    def __create_factory(self, type_: ElType):
        factory_class = get_factory_class(type_)
        self.__current_factories[type_] = factory_class(
            url=get_url(self.__current_tag),
            category_name=self.__current_names[ElType.CATEGORY],
            subcategory_name=self.__current_names[ElType.SUBCATEGORY],
            group_name=self.__current_names[ElType.GROUP]
        )