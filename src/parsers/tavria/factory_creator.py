"""Tag data collector."""
from collections import defaultdict, deque
from typing import Iterable

from bs4.element import Tag

from project_typing import ElType
from project_typing import folder_types

from sqlalchemy.orm import Session

from . import utils as u
from .object_box import ObjectBox
from .factory import BaseFactory, FolderFactory, ProductFactory


class FactoryCreator:
    """
    Makes request to source url.
    Parses tags, extracts data.
    Prapares data for objects creation.
    """
    _tags: Iterable[Tag]
    _current_tag: Tag
    _current_names = dict.fromkeys(folder_types)
    _current_factories: dict[ElType, BaseFactory] = {}
    _factories: defaultdict[ElType, deque[BaseFactory]]\
        = defaultdict(deque)

    def __init__(self, home_url: str) -> None:
        """TODO: Home url should be taken from retailer db object."""
        self._tags = u.get_catalog_tags(home_url)

    def __call__(self, db_session: Session) -> defaultdict[ElType, deque[BaseFactory]]:
        BaseFactory.object_box = ObjectBox(db_session)
        self._current_factories[ElType.CATEGORY]\
            = FolderFactory(ElType.CATEGORY)
        self.__create_factories()
        self.__close_last_factories()

        s = set()
        for _ in self._factories[ElType.GROUP]:
            if _ not in s:
                s.add(_)
            else:
                print(_)


        assert len(self._factories[ElType.GROUP])\
            == len(set(self._factories[ElType.GROUP]))
        return self._factories

    def __create_factories(self) -> None:
        """Prepare catalog factories from site information."""

        for tag in self._tags:
            if self.__tag_can_be_processed(tag_type := u.get_tag_type(tag)):  # noqa: E501
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

    def __recreate_factory(self, type_: ElType) -> None:
        if self.__this_factory_not_exists(type_):
            self.__close_factory(type_)
            self._create_factory(type_)

    def __this_factory_not_exists(self, type_: ElType) -> bool:
        """Will return True if current names are
        not equal to current factory parent names."""

        try:
            return not self.__check_factory(type_)
        except KeyError:
            return True

    def __check_factory(self, type_: ElType) -> bool:
        parent_names = tuple(self._current_names[_] if _ is not type_ else None
                             for _ in folder_types)
        return hash(parent_names) == hash(self._current_factories[type_])

    def __close_factory(self, type_: ElType) -> None:
        if self.__factory_is_ok(type_):
            self._factories[type_].append(self._current_factories.pop(type_))

    def __factory_is_ok(self, type_: ElType) -> bool:
        return bool(self._current_factories.get(type_, None))

    def _create_factory(self, type_: ElType):
        schema = u.get_schema_for(type_)
        init_payload = schema(
            el_type=type_,
            category_name=self._current_names[ElType.CATEGORY],
            subcategory_name=self._current_names[ElType.SUBCATEGORY],
            group_name=self._current_names[ElType.GROUP],
            url=u.get_url(self._current_tag)
        )
        create_cls = ProductFactory if type_ is ElType.PRODUCT\
            else FolderFactory
        self._current_factories[type_] = create_cls(**init_payload.dict())

    def __close_last_factories(self) -> None:
        for _ in ElType:
            self.__close_factory(_)
