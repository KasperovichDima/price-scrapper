"""Test mocks and changes to allow testing."""
from typing import Callable

from parsers.tavria import FactoryCreator
from parsers.tavria import factory as f
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


class ProductFactory_test(f.ProductFactory):

    async def get_page_html(self) -> None:
        self._html = html_for(self._url)


def __create_class_getter() -> Callable[[ElType], type[f.BaseFactory]]:
    types: dict[ElType, type[f.BaseFactory]] = {
        ElType.CATEGORY: f.CategoryFactory,
        ElType.SUBCATEGORY: f.SubcategoryFactory,
        ElType.GROUP: f.GroupFactory,
        ElType.PRODUCT: ProductFactory_test
    }

    def get_class(type_: ElType) -> type[f.BaseFactory]:
        return types[type_]
    return get_class


class_for = __create_class_getter()


class FactoryCreator_test(FactoryCreator):

    def _create_factory(self, type_: ElType):
        self._current_factories[type_] = class_for(type_)(
            url=u.get_url(self._current_tag),
            category_name=self._current_names[ElType.CATEGORY],
            subcategory_name=self._current_names[ElType.SUBCATEGORY],
            group_name=self._current_names[ElType.GROUP]
        )
