"""FactoryCreator class."""
from collections import deque

from . import utils as u
from .tavria_typing import Factory_P, Retailer_P


class FactoryCreator:
    """Implementation of FactoryCreator protocol."""
    _factories: deque[Factory_P] = deque()

    def __init__(self, retailer: Retailer_P,
                 factory_cls: type[Factory_P]) -> None:
        self.retailer = retailer
        self._factory_cls = factory_cls

    def create(self) -> deque[Factory_P]:
        for tag in u.get_group_tags(self.retailer.home_url):
            if url := u.get_url(tag):
                factory = self._factory_cls(url, self.retailer.id)
                self._factories.append(factory)

        self._remove_discount_page()
        return self._factories

    def _remove_discount_page(self) -> None:
        if 'discount' in str(self._factories[0]):
            self._factories.popleft()
