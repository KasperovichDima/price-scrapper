"""Tag data collector."""
from collections import defaultdict, deque
from typing import Iterable

from bs4.element import Tag

from project_typing import ElType

from pydantic import ValidationError

from .factories import BaseFactory
from .factories import CategoryFactory
from .factories import get_factory_class
from .utils import get_catalog_tags
from .utils import get_tag_type
from .utils import get_url
from .utils import group_is_outstanding


class FactoryCreator:
    """
    Makes request to source url.
    Parses tags, extracts data.
    Prapares data for objects creation.
    """
    __tags: Iterable[Tag]
    __current_tag: Tag
    __current_names = dict.fromkeys(ElType)
    __current_factories: dict[ElType, BaseFactory] = {}
    __factories: defaultdict[ElType, deque[BaseFactory]]\
        = defaultdict(deque)

    def __init__(self, home_url: str) -> None:
        self.__tags = get_catalog_tags(home_url)
        self.__current_factories[ElType.CATEGORY] = CategoryFactory()

    def __call__(self) -> defaultdict[ElType, deque[BaseFactory]]:
        self.__create_factories()
        self.__close_last_factories()

        return self.__factories

    def __create_factories(self) -> None:
        """Prepare catalog factories from site information."""

        for tag in self.__tags:
            if not self.__tag_can_be_processed(tag_type := get_tag_type(tag)):
                continue
            self.__current_tag = tag
            self.__process_tag(tag_type)  # type: ignore

    def __tag_can_be_processed(self, tag_type: ElType | None = None) -> bool:
        return tag_type in self.__current_factories

    def __process_tag(self, tag_type: ElType) -> None:
        self.__change_current_name(tag_type)

        if tag_type is ElType.CATEGORY:
            self.__try_to_create_factory(ElType.SUBCATEGORY)
            self.__try_to_create_factory(ElType.GROUP)

        elif tag_type is ElType.SUBCATEGORY:
            self.__try_to_create_factory(ElType.GROUP)

        elif tag_type is ElType.GROUP:
            if group_is_outstanding(self.__current_tag):
                self.__current_names[ElType.SUBCATEGORY] = None
                self.__try_to_create_factory(ElType.GROUP)
            self.__try_to_create_factory(ElType.PRODUCT)

        self.__current_factories[tag_type]\
            .add_name(self.__current_tag.text.strip())

    def __change_current_name(self, type_: ElType) -> None:
        self.__current_names[type_] = self.__current_tag.text.strip()

    def __try_to_create_factory(self, type_: ElType):
        self.__close_factory(type_)
        try:
            self.__create_factory(type_)
        except ValidationError:
            pass

    def __close_factory(self, type_: ElType) -> None:
        if self.__factory_is_ready_to_close(type_):
            self.__factories[type_].append(self.__current_factories.pop(type_))

    def __factory_is_ready_to_close(self, type_: ElType) -> bool:
        try:
            assert self.__current_factories[type_]
            return True
        except (KeyError, AssertionError):
            return False

    def __create_factory(self, type_: ElType):
        self.__current_factories[type_] = get_factory_class(type_)(
            url=get_url(self.__current_tag),
            category_name=self.__current_names[ElType.CATEGORY],
            subcategory_name=self.__current_names[ElType.SUBCATEGORY],
            group_name=self.__current_names[ElType.GROUP]
        )

    def __close_last_factories(self) -> None:
        for _ in ElType:
            self.__close_factory(_)
