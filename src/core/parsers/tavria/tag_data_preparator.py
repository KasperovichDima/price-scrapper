"""Tag data collector."""
from collections import defaultdict, deque
from typing import Iterable

from bs4.element import Tag

from project_typing import ElType

from .utils import get_catalog_tags
from .utils import tag_is_not_interesting
from .utils import get_type
from ...schemas import CatalogFactory


class TagDataPreparator:
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

    def __init__(self) -> None:
        self.__factories[ElType.CATEGORY].append(CatalogFactory())
        self.__current_factories[ElType.CATEGORY]\
            = self.__factories[ElType.CATEGORY][0]

    def __call__(self,
                 home_url: str) -> defaultdict[ElType, deque[CatalogFactory]]:
        self.__tags = get_catalog_tags(home_url)
        self.__prepare_objects_data()
        return self.__factories

    def __prepare_objects_data(self) -> None:
        """Prepare folder data from site information."""

        for tag in self.__tags:
            if tag_is_not_interesting(tag):
                continue
            self.__current_tag = tag
            self.__try_to_add()

    def __try_to_add(self) -> None:
        try:
            self.__add()
        except (AssertionError, KeyError):
            pass

    def __add(self) -> None:
        type_ = get_type(self.__current_tag)
        assert type_
        self.__change_current_name(type_)

        if type_ is ElType.CATEGORY:
            self.__recreate_factory(ElType.SUBCATEGORY)

        elif type_ is ElType.SUBCATEGORY:
            self.__recreate_factory(ElType.GROUP)

        elif type_ is ElType.GROUP:
            if self.__current_tag.parent.name == 'h4':
                self.__current_names[ElType.SUBCATEGORY] = None
                self.__recreate_factory(ElType.GROUP)
            self.__recreate_product_factory()

        self.__current_factories[type_].add_name(self.__current_tag.text.strip())

    def __change_current_name(self, type_: ElType) -> None:
        self.__current_names[type_] = self.__current_tag.text.strip()

    def __recreate_factory(self, type_: ElType) -> None:
        self.__try_to_close_factory(type_)
        self.__create_factory(type_)

    def __recreate_product_factory(self) -> None:
        self.__create_factory(ElType.PRODUCT)
        self.__try_to_close_factory(ElType.PRODUCT)

    @property
    def __current_url(self):
        try:
            url = self.__current_tag.get('href').strip()
            assert 'catalog' in url
            return url
        except (KeyError, AssertionError, AttributeError):
            return None

    def __try_to_close_factory(self, type_: ElType) -> None:
        if type_ not in self.__current_factories or (type_ is not ElType.PRODUCT and self.__current_factories[type_].is_empty):
            print(type_, self.__current_tag.text.strip())
        try:
            self.__close_factory(type_)
        except KeyError:
            pass

    def __close_factory(self, type_: ElType) -> None:
        self.__factories[type_].append(self.__current_factories.pop(type_))

    def __create_factory(self, type_: ElType):
        self.__current_factories[type_] = CatalogFactory(
            url=self.__current_url if type_ is ElType.PRODUCT else None,
            category_name=self.__current_names[ElType.CATEGORY],
            subcategory_name=self.__current_names[ElType.SUBCATEGORY] if type_ not in {ElType.CATEGORY, ElType.SUBCATEGORY} else None,
            group_name=self.__current_names[ElType.GROUP] if type_ is ElType.PRODUCT else None,
        )
