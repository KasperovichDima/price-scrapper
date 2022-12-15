"""Tavria V parser."""
from collections import defaultdict
from typing import Iterable

from bs4 import BeautifulSoup as bs
from bs4.element import Tag

from catalog.models import Folder

import crud

from database import SessionLocal

from project_typing import ElType

from .tree_builder import TreeBuilder
from .utils import get_catalog_tags
from ...constants import MAIN_PARSER

# 1. Get last level links
# 2. Grab products and prices with async
# 3. Grab new products
# 4. Save results to db


class TavriaParser:
    """Tavria V parser."""

    __cat_tags: Iterable[Tag]

    def __init__(self, home_url: str) -> None:
        self.__cat_tags = get_catalog_tags(home_url)


        # self.__get_last_level_links()
        # self.__collect_prices()
        # self.__save_new_products()
        # self.__save_results()
        return self.__completed_report


    def __get_last_level_links(self) -> None:

        links = (_ for _ in self.__cat_tags.find_all('a'))

        grand_parent: str = ''  # TODO: rename
        middle_parent: str = ''  # TODO: rename
        links_by_categories: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
        for _ in links:
            if text := _.string:
                links_by_categories[grand_parent].append((text.strip(), _.get('href')))
            elif _.get('href') == '#':
                grand_parent = _.text.strip()
            else:
                print(f'Skiping {_}...')

        # unwanted = ('Новий рік', 'Кулінарія')
        # for _ in unwanted:
        #     links_by_categories.pop(_)

        for k, v in links_by_categories.items():
            print(k + ':')
            for _ in v:
                print(_)
            print('\n\n')


    def __collect_prices(self) -> None:
        ...

    def __save_new_products(self) -> None:
        ...

    def __save_results(self) -> None:
        ...

    @property
    def __completed_report(self) -> None:
        ...
