"""Core validation schamas."""
from collections import deque
from datetime import datetime
from decimal import Decimal
from typing import Iterable

from catalog.models import Folder, Product
from catalog.schemas import BaseCatScheme, FolderScheme, ProductScheme

from interfaces import ICatalogElement

from project_typing import ElType

from pydantic import BaseModel, Field

from retailer.schemas import RetailerScheme


class RequestInScheme(BaseModel):
    """Edit request data scheme."""
    folders: list[int] = []
    products: list[int] = []
    retailers: list[int] = []


class RequestOutScheme(BaseModel):
    """Request content scheme."""

    folders: list[BaseCatScheme] = []
    products: list[BaseCatScheme] = []
    retailers: list[RetailerScheme] = []


class ReportHeaderScheme(BaseModel):
    """Validation of required user data for report header."""

    name: str = Field(max_length=100)
    note: str = Field(max_length=250)
    time_created: datetime = datetime.now()
    user_name: str | None


class PriceLineSchema(BaseModel):
    """Price line scheme."""

    product_id: int
    retailer_id: int
    retail_price: Decimal
    promo_price: Decimal

    class Config:
        orm_mode = True


class ReportScheme(BaseModel):
    """Complete report scheme."""

    header: ReportHeaderScheme
    folders: list[FolderScheme]
    products: list[ProductScheme]
    retailers: list[RetailerScheme]
    content: list[PriceLineSchema]


class CatalogFactory(BaseModel):
    """Contains all required information for catalog objects
    cretion. Creates objects using create_objects method."""

    obj_type: ElType
    url: str | None = None
    category_name: str | None = None
    subcategory_name: str | None = None
    group_name: str | None = None
    # parent_id: int | None
    # folders: Iterable[Folder]

    object_names: deque[str] = deque()  # TODO: Add special annotation to convert to simple attribute or make __

    def __bool__(self) -> bool:
        return bool(self.object_names)

    def add_name(self, name: str) -> None:
        self.object_names.append(name)

    def get_objects(self, parent_id: int) -> Iterable[ICatalogElement]:
        class_ = self.__get_class()
        return (class_(name=_, type=self.obj_type, parent_id=parent_id)
                for _ in self.object_names)

    def __get_class(self) -> type[ICatalogElement]:
        return Product if self.obj_type is ElType.PRODUCT else Folder


    # def get_objects(self, folders: Iterable[Folder]) -> Iterable[ICatalogElement]:
    #     self.folders = folders
    #     class_ = self.__get_class()
    #     self._get_parent_id()
    #     return (class_(name=_, type=self.obj_type, parent_id=self.parent_id)
    #             for _ in self.object_names)

#     def __get_class(self) -> type[ICatalogElement]:
#         return Product if self.obj_type is ElType.PRODUCT else Folder

#     def _get_parent_id(self) -> None:
#         ...

    
# class SubgroupFactory(CatalogFactory):

#     def _get_parent_id(self) -> None:
#         self.parent_id = next(_ for _ in self.folders if _.name == self.category_name)


# class GroupFactory(CatalogFactory):

#     def _get_parent_id(self) -> None:
#         cat_id = {_.name: _.id for _ in self.folders if _.type is ElType.CATEGORY}[self.category_name]
#         self.parent_id = {_.name: _.id for _ in self.folders if _.type is ElType.SUBCATEGORY and _.parent_id == cat_id}[self.subcategory_name]


# class ProductFactory(CatalogFactory):

#     def _get_parent_id(self) -> None:
#         cat_id = {_.name: _.id for _ in self.folders if _.type is ElType.CATEGORY}[self.category_name]
#         subcat_id = {_.name: _.id for _ in self.folders if _.type is ElType.SUBCATEGORY and _.parent_id == cat_id}[self.subcategory_name]
#         self.parent_id = {_.name: _.id for _ in self.folders if _.type is ElType.GROUP and _.parent_id == subcat_id}[self.group_name]

