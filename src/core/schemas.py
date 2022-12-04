"""Core validation schamas."""
from typing import Iterable

from constants import CATALOG_NAMES, RETAILER_NAMES

from project_typing import cat_elements

from pydantic import BaseModel, validator


class RequestDataScheme(BaseModel):
    """RequestData  validation scheme."""

    el_ids: cat_elements | None
    ret_names: list[str] | None

    @validator('el_ids')
    def catalog_names_alloved(cls, names: cat_elements):
        RequestDataScheme.__check_names(names, CATALOG_NAMES, 'catalog')
        return names

    @validator('ret_names')
    def retailer_names_alloved(cls, names: list[str]):
        RequestDataScheme.__check_names(names, RETAILER_NAMES, 'retailer')
        return names

    class Config:
        orm_mode = True

    @staticmethod
    def __check_names(names: Iterable[str], source: frozenset[str], type: str):
        """
        Checks, that 'type' names are in'source'. If not - raises exception.
        """
        if not names:
            return
        for name in names:
            if name not in source:
                raise ValueError(f'Incorrect {type} name: "{name}".')
