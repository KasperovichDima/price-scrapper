from typing import Any

from .price_factory import PriceFactory


class PriceParser:

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
