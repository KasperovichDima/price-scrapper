"""Test mocks and changes to allow testing."""
from typing import Callable

from parsers.tavria import BaseFactory
from parsers.tavria.new_factory_creator import FactoryCreator as NFC
from parsers.tavria import FolderFactory
from parsers.tavria import ProductFactory
from parsers.tavria import utils as u

from project_typing import ElType

from .html import groups as g


def __create_html_getter() -> Callable[[str], str]:
    html = dict(
        catalog_buckwheat=g.catalog_buckwheat,
        catalog_corn=g.catalog_corn,
        catalog_empty=g.catalog_empty,
        catalog_fast_food=g.catalog_fast_food,
        catalog_protein=g.catalog_protein,
        catalog_rice=g.catalog_rice,
    )
    html['catalog_fast_food?page=2'] = g.catalog_fast_food_2
    html['catalog_fast_food?page=3'] = g.catalog_fast_food_3

    def get_html(url: str) -> str:
        return html[url]
    return get_html


html_for = __create_html_getter()


class ProductFactory_test(ProductFactory):

    async def get_page_html(self) -> None:
        assert self._url
        self._html = html_for(self._url)


class FactoryCreator_test(NFC):

    def create_factory(self) -> BaseFactory:
        schema = u.get_schema_for(self._tag_type)
        init_payload = schema(
            el_type=self._tag_type,
            category_name=self._current_names[ElType.CATEGORY],
            subcategory_name=self._current_names[ElType.SUBCATEGORY],
            group_name=self._current_names[ElType.GROUP],
            url=u.get_url(self._tag)
        )
        create_cls = ProductFactory_test if self._tag_type is ElType.PRODUCT\
            else FolderFactory
        return create_cls(**init_payload.dict())