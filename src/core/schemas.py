"""Core validation schamas."""
from collections import deque
from datetime import datetime
from decimal import Decimal
from typing import Iterable

from catalog.models import Product
from catalog.schemas import BaseCatScheme, FolderScheme, ProductScheme

from interfaces import ICatalogElement

from pydantic import BaseModel, Field

from project_typing import ElType

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
    cretion. Creates folders using create_objects method."""

    def create_objects(self) -> Iterable[ICatalogElement]:
        ...


class FolderFactory(CatalogFactory):

    name: str
    parent_name: str | None = None
    parent_type: ElType | None = None


class ProductFactory(CatalogFactory):
    """Contains all required information for catalog objects
    cretion. Creates folders using create_objects method."""

    parent_url: str
    category_name: str
    subcategory_name: str
    group_name: str
    parent_id: int | None
    product_names: deque[str] = deque()

    def create_objects(self) -> Iterable[Product]:
        if not self.parent_id:
            raise KeyError('Can not create products without parent id.')
        return (Product(name=_, parent_id=self.parent_id)
                for _ in self.product_names)
