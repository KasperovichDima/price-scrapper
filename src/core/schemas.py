"""Core validation schamas."""
from datetime import datetime
from decimal import Decimal

from catalog.schemas import BaseCatScheme, FolderScheme, ProductScheme

from pydantic import BaseModel, Field

from retailer.schemas import RetailerScheme


class RequestInScheme(BaseModel):
    """Edit request data scheme."""
    folders: list[int] = Field(default_factory=list)
    products: list[int] = Field(default_factory=list)
    retailers: list[int] = Field(default_factory=list)


class RequestOutScheme(BaseModel):
    """Request content scheme."""

    folders: list[BaseCatScheme] = Field(default_factory=list)
    products: list[BaseCatScheme] = Field(default_factory=list)
    retailers: list[RetailerScheme] = Field(default_factory=list)


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
