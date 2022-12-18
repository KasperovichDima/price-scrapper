"""Tag data collector."""
from collections import defaultdict, deque
from typing import Iterable

from bs4.element import Tag

from project_typing import ElType

from pydantic import ValidationError

from .utils import get_catalog_tags
from .utils import tag_is_a_category
from .utils import tag_is_a_group
from .utils import tag_is_a_subcategory
from ...schemas import CatalogFactory
from ...schemas import FolderFactory
from ...schemas import ProductFactory


class TagDataPreparator:
    """
    Makes request to source url.
    Parses tags, extracts data.
    Prapares data for objects creation.
    """
    __tags: Iterable[Tag]
    __current_tag: Tag
    __current_cat_name: str | None = None
    __current_subcat_name: str | None = None
    __factories: defaultdict[ElType, deque[CatalogFactory]]\
        = defaultdict(deque)

    def __init__(self, home_url: str) -> None:
        self.__tags = get_catalog_tags(home_url)

        self.__prepare_objects_data()

    def __prepare_objects_data(self) -> None:
        """Prepare folder data from site information."""

        for tag in self.__tags:
            self.__current_tag = tag
            if tag_is_a_group(tag):
                self.__add_group_data()
            elif tag_is_a_subcategory(tag):
                self.__add_subcategory_data()
            elif tag_is_a_category(tag):
                self.__add_category_data()
            else:
                continue

    def __add_group_data(self) -> None:
        (parent_name, parent_type)\
            = (self.__current_cat_name, ElType.CATEGORY)\
            if not self.__current_subcat_name\
            or tag_is_a_subcategory(self.__current_tag)\
            else (self.__current_subcat_name, ElType.SUBCATEGORY)
        if parent_name:
            folder_data = FolderFactory(name=self.__current_tag.text.strip(),
                                        parent_name=parent_name,
                                        parent_type=parent_type)
            self.__factories[ElType.GROUP].append(folder_data)
        self.__try_to_add_product_factory()

    def __add_subcategory_data(self) -> None:
        self.__current_subcat_name = self.__current_tag.text.strip()
        self.__factories[ElType.SUBCATEGORY]\
            .append(FolderFactory(name=self.__current_subcat_name,
                                  parent_name=self.__current_cat_name,
                                  parent_type=ElType.CATEGORY))
        self.__try_to_add_product_factory()

    def __add_category_data(self) -> None:
        self.__current_cat_name = self.__current_tag.text.strip()
        self.__current_subcat_name = None  # TODO: Try to remove this.
        self.__factories[ElType.CATEGORY]\
            .append(FolderFactory(name=self.__current_cat_name))

    def __try_to_add_product_factory(self) -> None:
        """Create product factory for every product group."""
        try:
            self.__add_product_factory()
        except (ValidationError, AssertionError):
            pass

    def __add_product_factory(self) -> None:
        assert self.__current_cat_name or self.__current_subcat_name
        factory = ProductFactory(parent_url=self.__current_tag.get('href'),
                                 category_name=self.__current_cat_name,
                                 subcategory_name=self.__current_subcat_name,
                                 group_name=self.__current_tag.text.strip())
        self.__factories[ElType.PRODUCT].append(factory)
