"""Tavria parser utils."""
from typing import Iterable
from urllib import request

from bs4 import BeautifulSoup as bs
from bs4.element import Tag


def get_catalog_tags(url: str) -> Iterable[Tag]:
    """Parses home page and returns parsed tags of catalog menu."""
    response = request.urlopen(url)
    return bs(response, 'lxml').find(
        'aside', {'class': 'col-md-3 sidebar__container'}
    ).find_all()


# def tag_is_not_interesting(tag: Tag) -> bool:
#     try:
#         return ('discount' in tag.get('href')
#                 or tag.is_empty_element)
#     except TypeError:
#         return False


def tag_is_a_group(tag: Tag) -> bool:
    return (tag.name == 'a'
            and 'catalog' in tag.get('href')
            and tag.parent.name == 'li')


def tag_is_a_subcategory(tag: Tag) -> bool:
    return (tag.name == 'span' and 'class' in tag.attrs
            and tag.attrs['class'][0] == 'top-sub-catalog-name')\
            or (tag.name == 'a' and tag.parent.name == 'h4')


def tag_is_a_category(tag: Tag) -> bool:
    return tag.name == 'a' and tag.get('href') == '#'
