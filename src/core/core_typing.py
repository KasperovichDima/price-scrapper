"""Core custom datatypes."""
from collections import deque, namedtuple
from typing import Iterable, NamedTuple

from catalog.models import Product

import interfaces as i


class RequestObjects(NamedTuple):
    """Objects to be added to request."""

    folders: list[i.IFolder]
    products: list[i.IProduct]
    retailers: list[i.IRetailer]


FolderData = namedtuple('FolderData', 'name parent_name parent_type',
                        defaults=(None, None))


# class ProductFactory:
#     """Contains all required information for product.
#     cretion. Creates products using 'products' property."""

#     parent_id: int

#     def __init__(self, url: str, category_name: str, subcategory_name: str, group_name: str) -> None:
#         self.__url = url
#         self. __category_name = category_name
#         self. __subcategory_name = subcategory_name
#         self.__group_name = group_name
#         self.__product_names: deque[str] = deque()

#     @property
#     def products(self) -> Iterable[Product]:
#         return (Product(name=_, parent_id=self.parent_id)
#         for _ in self.__product_names)
