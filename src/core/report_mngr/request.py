"""Request class."""
from catalog.models import Folder, Product

from retailer.models import Retailer

from ..core_typing import RequestObjects
from ..schemas import RequestOutScheme


class Request:
    """Request for new report. Contain all required information: products,
    folders, retailers. Also provides request operations, like get, add,
    remove request data."""

    def __init__(self) -> None:
        self.__folders: set[Folder] = set()
        self.__products: set[Product] = set()
        self.__retailers: set[Retailer] = set()

    def __bool__(self):
        return bool((self.__products or self.__folders) and self.__retailers)

    @property
    def folders(self) -> list[Folder]:
        return sorted(list(self.__folders), key=lambda _: _.name)

    @property
    def products(self) -> list[Product]:
        return sorted(list(self.__products), key=lambda _: _.name)

    @property
    def retailers(self) -> list[Retailer]:
        return sorted(list(self.__retailers), key=lambda _: _.name)

    @property
    def out_data(self) -> RequestOutScheme:
        """Pydantic model of current request."""
        return RequestOutScheme(folders=self.folders,
                                products=self.products,
                                retailers=self.retailers)

    def add_objects(self, data: RequestObjects) -> None:
        """Add objects to current request."""

        self.__products.update(data.products)
        self.__folders.update(data.folders)
        self.__retailers.update(data.retailers)

    def remove_objects(self, data: RequestObjects) -> None:
        """Remove objects from current request."""

        self.__products.difference_update(data.products)
        self.__folders.difference_update(data.folders)
        self.__retailers.difference_update(data.retailers)
