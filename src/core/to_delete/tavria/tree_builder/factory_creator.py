"""Tag data collector."""
from collections import defaultdict, deque
from typing import Iterable

from bs4.element import Tag

from project_typing import ElType

from . import utils as u
from .factories import BaseFactory
from .factories import CategoryFactory


class FactoryCreator:
    """
    Makes request to source url.
    Parses tags, extracts data.
    Prapares data for objects creation.
    """
    __tags: Iterable[Tag]
    _current_tag: Tag
    _current_names = dict.fromkeys(ElType)
    _current_factories: dict[ElType, BaseFactory] = {}
    __factories: defaultdict[ElType, deque[BaseFactory]]\
        = defaultdict(deque)

    def __init__(self, home_url: str) -> None:
        self.__tags = u.get_catalog_tags(home_url)
        self._current_factories[ElType.CATEGORY] = CategoryFactory()

    def __call__(self) -> defaultdict[ElType, deque[BaseFactory]]:
        self.__create_factories()
        self.__close_last_factories()

        return self.__factories

    def __create_factories(self) -> None:
        """Prepare catalog factories from site information."""

        for tag in self.__tags:
            if not self.__tag_can_be_processed(tag_type := u.get_tag_type(tag)):  # noqa: E501
                continue
            self._current_tag = tag
            self.__process_tag(tag_type)  # type: ignore

    def __tag_can_be_processed(self, tag_type: ElType | None = None) -> bool:
        return tag_type in self._current_factories

    def __process_tag(self, tag_type: ElType) -> None:
        self.__change_current_name(tag_type)

        if tag_type is ElType.CATEGORY:
            self.__recreate_factory(ElType.SUBCATEGORY)
            self.__recreate_factory(ElType.GROUP)

        elif tag_type is ElType.SUBCATEGORY:
            self.__recreate_factory(ElType.GROUP)

        elif tag_type is ElType.GROUP:
            if u.group_is_outstanding(self._current_tag):
                self._current_names[ElType.SUBCATEGORY] = None
                self.__recreate_factory(ElType.GROUP)
            self.__recreate_factory(ElType.PRODUCT)

        self._current_factories[tag_type]\
            .add_name(self._current_tag.text.strip())

    def __change_current_name(self, type_: ElType) -> None:
        self._current_names[type_] = self._current_tag.text.strip()

    def __recreate_factory(self, type_: ElType):
        self.__close_factory(type_)
        self._create_factory(type_)

    def __close_factory(self, type_: ElType) -> None:
        if self.__factory_is_ready_to_close(type_):
            self.__factories[type_].append(self._current_factories.pop(type_))

    def __factory_is_ready_to_close(self, type_: ElType) -> bool:
        try:
            assert self._current_factories[type_]
            return True
        except (KeyError, AssertionError):
            return False

    def _create_factory(self, type_: ElType):
        self._current_factories[type_] = u.class_for(type_)(
            url=u.get_url(self._current_tag),
            category_name=self._current_names[ElType.CATEGORY],
            subcategory_name=self._current_names[ElType.SUBCATEGORY],
            group_name=self._current_names[ElType.GROUP]
        )

    def __close_last_factories(self) -> None:
        for _ in ElType:
            self.__close_factory(_)
