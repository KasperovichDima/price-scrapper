"""Test mocks and changes to allow testing."""
from parsers.tavria.price_parser import PriceFactory

from .html import groups as g


mocked_pages: dict[str, str] = dict(
    catalog_buckwheat=g.catalog_buckwheat,
    catalog_corn=g.catalog_corn,
    catalog_rice=g.catalog_rice,
    catalog_protein=g.catalog_protein,
    catalog_fast_food=g.catalog_fast_food,
    catalog_chips=g.catalog_chips,
)
mocked_pages['catalog_rice?page=2'] = g.catalog_rice_2
mocked_pages['catalog_rice?page=3'] = g.catalog_rice_3


class PriceFactory_test(PriceFactory):
    """Mock class for testing with changed _get_page_html method"""

    async def _get_page_html(self) -> str | None:
        return mocked_pages[self._url]
