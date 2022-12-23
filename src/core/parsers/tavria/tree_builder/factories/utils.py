"""get_factory_class function."""
from typing import Callable

from project_typing import ElType

from .base_factory import BaseFactory
from .folder_factory import CategoryFactory
from .folder_factory import GroupFactory
from .folder_factory import SubcategoryFactory
from .product_factory import ProductFactory


def __create_class_getter() -> Callable[[ElType], type[BaseFactory]]:
    types: dict[ElType, type[BaseFactory]] = {
        ElType.CATEGORY: CategoryFactory,
        ElType.SUBCATEGORY: SubcategoryFactory,
        ElType.GROUP: GroupFactory,
        ElType.PRODUCT: ProductFactory
    }

    def get_class(type_: ElType) -> type[BaseFactory]:
        return types[type_]
    return get_class


factory_for = __create_class_getter()
