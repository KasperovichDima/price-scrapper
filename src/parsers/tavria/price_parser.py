from typing import Any

from .price_factory import PriceFactory


class PriceParser:

    """
    1. get links.
    2. get factories for them.
    3. each factory saves parents names.
    4. get exisiting price lines of current factory
       group by id, calculated by parents names.
    5. remove from factory results all members, that
       are equal to existing price records in db.
    6. Update records, that have diff prices, delete
       them from factory results.
    6. If something left in factory result members -
       load products from db by parent id and names.
    7. Get ids of this products.
    8. Create new price lines for this products.
    """

    factory_creator_class: Any
    factories: list[PriceFactory]

    def refresh_prices(self) -> None:
        self.get_factories()
        self.save_prices()

    def get_factories(self) -> None:
        self.factories = self.factory_creator_class()()

    def save_prices(self) -> None:
        for factory in self.factories:
            factory()
