"""Tavria V parser."""
from bs4 import BeautifulSoup as bs
from bs4.element import Tag
from typing import Iterable
from urllib import request
from collections import defaultdict, namedtuple
from project_typing import CatType
from database import SessionLocal
import crud
from catalog.models import Folder
from ..constants import MAIN_PARSER


# 1. Get last level links
# 2. Grab products and prices with async
# 3. Grab new products
# 4. Save results to db


class TavriaParser:
    """Tavria V parser."""

    __catalog: Iterable[Tag]
    __start_page_url = 'https://www.tavriav.ua/'

    def __init__(self) -> None:
        self.__get_catalog()
        self.__create_catalog_tree()
        # self.__get_last_level_links()
        # self.__collect_prices()
        # self.__save_new_products()
        # self.__save_results()
        return self.__completed_report

    def __get_catalog(self):
        response = request.urlopen(self.__start_page_url)
        self.__catalog = bs(response, 'lxml').find(
            'aside', {'class': 'col-md-3 sidebar__container'}
        ).find_all()

    def __create_catalog_tree(self):
        """TODO: switch."""
        if MAIN_PARSER != 'Tavria':
            return

        category = subcategory = parent_type = None
        el_data = namedtuple('el_data', 'name type parent_name parent_type', defaults=(None, None))
        el_ts: list[el_data] = []

        elements: defaultdict[tuple[CatType, str], list[tuple[CatType, str]]] = defaultdict(list)
        for _ in self.__catalog:

            if _.name not in ('a', 'span'):
                continue

            elif _.name == 'a':
                if _.get('href') == '#':
                    category = _.text.strip()
                    subcategory = None
                    #
                    el_ts.append(el_data(category, CatType.CATEGORY))

                elif 'catalog' in _.get('href'):
                    parent = category if not subcategory or _.parent.name == 'h4' else subcategory
                    elements[(parent_type, parent)].append((CatType.GROUP, _.text.strip()))
                    #
                    parent_type = CatType.CATEGORY if not subcategory or _.parent.name == 'h4' else CatType.SUBCATEGORY
                    el_ts.append(el_data(_.text.strip(), CatType.GROUP, parent, parent_type))

            elif _.name == 'span' and 'class' in _.attrs and _.attrs['class'][0] == 'top-sub-catalog-name':
                subcategory = _.text.strip()
                elements[category].append(subcategory)
                #
                el_ts.append(el_data(subcategory, CatType.SUBCATEGORY, category, CatType.CATEGORY))

        with SessionLocal() as session:
            crud.add_instances(
                (Folder(name=_.name, type=_.type) for _ in el_ts if _.type == CatType.CATEGORY),
                session)
            cat_names = (_.name for _ in el_ts if _.type == CatType.CATEGORY)
            categories = session.query(Folder).filter(Folder.name.in_(cat_names)).all()
            cat_name_to_id = {_.name: _.id for _ in categories}
            subcategories = (Folder(name=_.name, type=_.type, parent_id=cat_name_to_id[_.parent_name]) for _ in el_ts if _.type == CatType.SUBCATEGORY)
            crud.add_instances(subcategories, session)
            subcats = session.query(Folder).filter(Folder.type == CatType.SUBCATEGORY).all()
            subcat_name_to_id = {_.name: _.id for _ in subcats}
            # groups = (Folder(name=_.name, type=CatType.GROUP, parent_id=cat_name_to_id[_.parent_name] if _.parent_type == CatType.CATEGORY else subcat_name_to_id[_.parent_name]) for _ in el_ts if _.type == CatType.GROUP)
            groups = []
            for _ in (el for el in el_ts if el.type == CatType.GROUP):
                try:
                    p_id = cat_name_to_id[_.parent_name]\
                        if _.parent_type == CatType.CATEGORY\
                        else subcat_name_to_id[_.parent_name]
                except KeyError:
                    continue
                folder = Folder(
                    name=_.name,
                    type=_.type,
                    parent_id=p_id
                )
                groups.append(folder)
            crud.add_instances(groups, session)
            pass
















    def __get_last_level_links(self) -> None:

        links = (_ for _ in self.__catalog.find_all('a'))

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
