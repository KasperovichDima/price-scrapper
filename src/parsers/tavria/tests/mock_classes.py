"""Test mocks and changes to allow testing."""
from typing import Callable

from parsers.tavria import BaseFactory
from parsers.tavria import FactoryCreator as CatalogFactoryCreator
from parsers.tavria import FolderFactory
from parsers.tavria import ProductFactory
from parsers.tavria import utils as u
from parsers.tavria.price_parser import FactoryCreator as PriceFactoryCreator
from parsers.tavria.price_parser import PriceFactory
from parsers.tavria.price_parser import PriceParser

from project_typing import ElType

from .html import groups as g
from .html import groups_v2 as g2


def __create_html_getter() -> Callable[[str], str]:
    html = dict(
        catalog_buckwheat=g.catalog_buckwheat,
        catalog_corn=g.catalog_corn,
        catalog_chips=g.catalog_chips,
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

    async def _get_page_html(self) -> None:
        assert self._url
        self._html = html_for(self._url)


class CatalogFactoryCreator_test(CatalogFactoryCreator):

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


mocked_pages: dict[str, str] = dict(
    catalog_buckwheat=g2.catalog_buckwheat,
    catalog_corn=g2.catalog_corn,
    catalog_rice=g2.catalog_rice,
    catalog_protein=g2.catalog_protein,
    catalog_fast_food=g2.catalog_fast_food,
    catalog_chips=g2.catalog_chips,
)
mocked_pages['catalog_rice?page=2'] = g2.catalog_rice_2
mocked_pages['catalog_rice?page=3'] = g2.catalog_rice_3


class PriceFactory_test(PriceFactory):
    """Mock class for testing with changed _get_page_html method"""

    async def _get_page_html(self) -> str | None:
        return mocked_pages[self._url]


class PriceFactoryCreator_test(PriceFactoryCreator):
    """Mock class for testing with changed create_factory method."""

    def create_factory(self, tag) -> None:
        """Should use PriceFactory_test class instead of PriceFactory."""
        self._factories.append(
            PriceFactory_test(u.get_url(tag), self.retailer_id)
        )


class PriceParser_test(PriceParser):
    """Mock class for testing with changed get_factories method."""

    def _get_factories(self) -> None:
        """Should use FactoryCreator_test class instead of FactoryCreator."""
        self._factories = PriceFactoryCreator_test()(self._retailer.home_url,
                                                     self._retailer.id)
