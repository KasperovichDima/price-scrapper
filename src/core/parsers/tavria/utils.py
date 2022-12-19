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


def tag_is_interesting(tag: Tag) -> bool:
    try:
        return tag.name in ('a', 'span')
    except KeyError:
        return False


def get_url(tag: Tag) -> str | None:
    try:
        url = tag.get('href').strip()
        assert 'catalog' in url
        return url
    except (KeyError, AssertionError, AttributeError):
        return None



def get_type(tag: Tag) -> ElType:
    if tag.name == 'a' and 'catalog' in tag.get('href'):
        return ElType.GROUP
    elif (tag.name == 'span' and 'class' in tag.attrs
          and tag.attrs['class'][0] == 'top-sub-catalog-name')\
            or (tag.name == 'a' and tag.parent.name == 'h4'):
        return ElType.SUBCATEGORY
    elif tag.name == 'a' and tag.get('href') == '#':
        return ElType.CATEGORY
    else:
        raise TypeError(f"{tag} does't match any catalog type.")
