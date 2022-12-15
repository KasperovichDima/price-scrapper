"""TreeBuilder class for creating catalog tree."""
from collections import deque
from functools import cached_property

from bs4.element import Tag

from catalog.models import Folder

import crud

from project_typing import ElType

from sqlalchemy.orm import Session

from .utils import get_catalog_tags
from .utils import tag_is_a_category
from .utils import tag_is_a_group
from .utils import tag_is_a_subcategory
from .utils import tag_is_not_interesting
from ...constants import MAIN_PARSER
from ...core_typing import FolderData


class TreeBuilder:
    """
    Check if catalog tree exists in database
    and update it with site information.
    TODO: slots.
    """

    __current_cat_name: str = ''
    __current_subcat_name: str = ''
    __new_groups: deque[FolderData] = deque()
    __new_subcategories: deque[FolderData] = deque()
    __new_categories: deque[FolderData] = deque()

    def __init__(self, home_url: str, session: Session) -> None:
        if MAIN_PARSER != 'Tavria':
            return

        self.__tags = get_catalog_tags(home_url)
        self.__session = session

        self.__collect_folders_data()

        self.__create_categories()
        self.__create_subcategories()
        self.__create_groups()

    def __collect_folders_data(self) -> None:
        """Prepare folder data from site information."""

        for tag in self.__tags:
            if tag_is_not_interesting(tag):
                continue
            elif tag_is_a_group(tag):
                self.__add_group_data(tag)
            elif tag_is_a_subcategory(tag):
                self.__add_subcategory_data(tag)
            elif tag_is_a_category(tag):
                self.__add_category_data(tag)
            else:
                continue

    def __add_group_data(self, tag: Tag) -> None:
        (parent, parent_type) = (self.__current_cat_name, ElType.CATEGORY)\
            if not self.__current_subcat_name or tag_is_a_subcategory(tag)\
            else (self.__current_subcat_name, ElType.SUBCATEGORY)
        self.__new_groups.append(FolderData(tag.text.strip(),
                                            parent, parent_type))

    def __add_subcategory_data(self, tag: Tag) -> None:
        self.__current_subcat_name = tag.text.strip()
        self.__new_subcategories.append(FolderData(self.__current_subcat_name,
                                                   self.__current_cat_name,
                                                   ElType.CATEGORY))

    def __add_category_data(self, tag: Tag) -> None:
        self.__current_cat_name = tag.text.strip()
        self.__current_subcat_name = ''
        self.__new_categories.append(FolderData(self.__current_cat_name))

    def __create_categories(self) -> None:
        """Creates Category objects in database."""
        crud.add_instances((Folder(name=_.name, type=ElType.CATEGORY)
                           for _ in self.__new_categories), self.__session)

    def __create_subcategories(self) -> None:
        """Creates Subcategories objects in database.
        Must be called after the categories are created."""
        subcategories = (Folder(name=_.name, type=ElType.SUBCATEGORY,
                                parent_id=self.__cat_name_id[_.parent_name])
                         for _ in self.__new_subcategories)
        crud.add_instances(subcategories, self.__session)

    def __create_groups(self) -> None:
        """Creates Group objects in database. Must be called
        after the categories and subcategories are created."""
        groups = (Folder(name=_.name, type=ElType.GROUP,
                         parent_id=self.__cat_name_id[_.parent_name]
                         if _.parent_type == ElType.CATEGORY
                         else self.__subcat_name_id[_.parent_name])
                  for _ in self.__new_groups)
        crud.add_instances(groups, self.__session)

    @cached_property
    def __cat_name_id(self) -> dict[str, int]:
        created_categories = crud.get_folders(
            self.__session, names=(_.name for _ in self.__new_categories)
        )
        return {_.name: _.id for _ in created_categories}

    @cached_property
    def __subcat_name_id(self) -> dict[str, int]:
        created_subcategories = crud.get_folders(
            self.__session, names=(_.name for _ in self.__new_subcategories)
        )
        return {_.name: _.id for _ in created_subcategories}
