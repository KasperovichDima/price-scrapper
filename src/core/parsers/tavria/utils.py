"""Tavria parser utils."""
from typing import Iterable
from urllib import request

from bs4 import BeautifulSoup as bs
from bs4.element import Tag

from project_typing import ElType


def get_catalog_tags(url: str) -> Iterable[Tag]:
    """Parses home page and returns parsed tags of catalog menu."""
    response = request.urlopen(url)
    return bs(response, 'lxml').find(
        'aside', {'class': 'col-md-3 sidebar__container'}
    ).find_all()


def tag_is_not_interesting(tag: Tag) -> bool:
    try:
        return tag.name not in ('a', 'span')
    except KeyError:
        return True


# def tag_is_a_group(tag: Tag) -> bool:
#     return tag.name == 'a' and 'catalog' in tag.get('href')


# def tag_is_a_subcategory(tag: Tag) -> bool:
#     return (tag.name == 'span' and 'class' in tag.attrs
#             and tag.attrs['class'][0] == 'top-sub-catalog-name')\
#         or (tag.name == 'a' and tag.parent.name == 'h4')


# def tag_is_a_category(tag: Tag) -> bool:
#     return tag.name == 'a' and tag.get('href') == '#'


def get_type(tag: Tag) -> ElType | None:
    if tag.name == 'a' and 'catalog' in tag.get('href'):
        return ElType.GROUP
    elif (tag.name == 'span' and 'class' in tag.attrs
            and tag.attrs['class'][0] == 'top-sub-catalog-name')\
        or (tag.name == 'a' and tag.parent.name == 'h4'):
        return ElType.SUBCATEGORY
    elif tag.name == 'a' and tag.get('href') == '#':
        return ElType.CATEGORY
    else:
        return None
