"""Core validation schamas."""
from project_typing import CatType

from pydantic import BaseModel

from retailer.schemas import RetailerScheme


class RequestInScheme(BaseModel):
    """Edit request data scheme."""
    folders: list[int] = []
    products: list[int] = []
    retailers: list[int] = []


class ElementScheme(BaseModel):
    """Base scheme for catalog element."""

    id: int
    name: str
    type: CatType

    class Config:
        orm_mode = True


class RequestOutScheme(BaseModel):
    """Request content scheme."""

    folders: list[ElementScheme] = []
    products: list[ElementScheme] = []
    retailers: list[RetailerScheme] = []
