"""TreeBuilder class for creating catalog tree."""
from collections import defaultdict, deque
from functools import cached_property

from bs4.element import Tag

from catalog.models import Folder

import crud

from project_typing import ElType

from pydantic import ValidationError

from sqlalchemy.orm import Session

from .utils import get_catalog_tags
from .utils import tag_is_a_category
from .utils import tag_is_a_group
from .utils import tag_is_a_subcategory
from ...constants import MAIN_PARSER
from ...core_typing import FolderData
from ...schemas import ProductFactory


class TreeBuilder:
    """
    Check if catalog tree exists in database
    and update it with site information.
    TODO: slots.
    """

    __current_cat_name: str = ''
    __current_subcat_name: str = ''
    __new_folders: defaultdict[ElType, deque[FolderData]] = defaultdict(deque)
    __product_factories: deque[ProductFactory] = deque()

    def __init__(self, home_url: str, session: Session) -> None:
        if MAIN_PARSER != 'Tavria':
            return

        self.__tags = get_catalog_tags(home_url)
        self.__session = session

        self.__collect_tags_data()

        self.__create_categories()
        self.__create_subcategories()
        self.__create_groups()
        self.__create_products()

    def __collect_tags_data(self) -> None:
        """Prepare folder data from site information."""

        cat_name = sub_name = ''

        def add_product_factory(tag: Tag) -> None:
            """Create product factory for every product group."""
            try:
                assert cat_name or sub_name
                factory = ProductFactory(url=tag.get('href'),
                                         category_name=cat_name,
                                         subcategory_name=sub_name,
                                         group_name=tag.text.strip())
                self.__product_factories.append(factory)
            except (ValidationError, AssertionError):
                pass

        for tag in self.__tags:
            if tag_is_a_group(tag):
                add_product_factory(tag)
                self.__add_group_data(tag)
            elif tag_is_a_subcategory(tag):
                sub_name = tag.text.strip()
                add_product_factory(tag)
                self.__add_subcategory_data(tag)
            elif tag_is_a_category(tag):
                cat_name, sub_name = tag.text.strip(), ''
                self.__add_category_data(tag)
            else:
                continue

    def __add_group_data(self, tag: Tag) -> None:
        (parent_name, parent_type)\
            = (self.__current_cat_name, ElType.CATEGORY)\
            if not self.__current_subcat_name or tag_is_a_subcategory(tag)\
            else (self.__current_subcat_name, ElType.SUBCATEGORY)
        if parent_name:
            self.__new_folders[ElType.GROUP].append(FolderData(tag.text.strip(),
                                                    parent_name, parent_type))

    def __add_subcategory_data(self, tag: Tag) -> None:
        self.__current_subcat_name = tag.text.strip()
        self.__new_folders[ElType.SUBCATEGORY]\
            .append(FolderData(self.__current_subcat_name,
                               self.__current_cat_name, ElType.CATEGORY))

    def __add_category_data(self, tag: Tag) -> None:
        self.__current_cat_name = tag.text.strip()
        self.__current_subcat_name = ''
        self.__new_folders[ElType.CATEGORY]\
            .append(FolderData(self.__current_cat_name))

    def __create_categories(self) -> None:
        """Creates Category objects in database."""
        categories = (Folder(name=_.name, type=ElType.CATEGORY)
                      for _ in self.__new_folders[ElType.CATEGORY])
        crud.add_instances(categories, self.__session)

    def __create_subcategories(self) -> None:
        """Creates Subcategories objects in database.
        Must be called after the categories are created."""
        subcategories = (Folder(name=_.name, type=ElType.SUBCATEGORY,
                                parent_id=self.__cat_name_id[_.parent_name])
                         for _ in self.__new_folders[ElType.SUBCATEGORY])
        crud.add_instances(subcategories, self.__session)

    def __create_groups(self) -> None:
        """Creates Group objects in database. Must be called
        after the categories and subcategories are created."""
        groups = (Folder(name=_.name, type=ElType.GROUP,
                         parent_id=self.__cat_name_id[_.parent_name]
                         if _.parent_type == ElType.CATEGORY
                         else self.__subcat_name_id[_.parent_name])
                  for _ in self.__new_folders[ElType.GROUP])
        crud.add_instances(groups, self.__session)

    def __create_products(self) -> None:
        """Creates Product objects in database. Must be called
        after the categories, subcategories and groups are created."""
        ...

    @cached_property
    def __cat_name_id(self) -> dict[str, int]:
        return {_.name: _.id for _ in self.__saved_categories}

    @cached_property
    def __saved_categories(self) -> list[Folder]:
        names = (_.name for _ in self.__new_folders[ElType.CATEGORY])
        return crud.get_folders(self.__session, names=names)

    @cached_property
    def __subcat_name_id(self) -> dict[str, int]:
        return {_.name: _.id for _ in self.__saved_subcategories}

    @cached_property
    def __saved_subcategories(self) -> list[Folder]:
        names = (_.name for _ in self.__new_folders[ElType.SUBCATEGORY])
        return crud.get_folders(self.__session, names=names)
