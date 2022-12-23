"""get_factory_class function."""
from project_typing import ElType

from .base_factory import BaseFactory
from .folder_factory import CategoryFactory
from .folder_factory import GroupFactory
from .folder_factory import SubcategoryFactory
from .product_factory import ProductFactory


__FACTORIES_TYPES: dict[ElType, type[BaseFactory]] = {
    ElType.CATEGORY: CategoryFactory,
    ElType.SUBCATEGORY: SubcategoryFactory,
    ElType.GROUP: GroupFactory,
    ElType.PRODUCT: ProductFactory
}


def get_factory_class(type_: ElType) -> type[BaseFactory]:
    """Get factory by element type."""
    return __FACTORIES_TYPES[type_]
