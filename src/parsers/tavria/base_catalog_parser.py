from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import MutableSequence, Type

from catalog.models import BaseCatalogElement

import crud

from parsers.constants import MAIN_PARSER

from project_typing import ElType

from sqlalchemy.orm import Session

from .factory import BaseFactory
from .tavria_typing import ObjectParents


class TavriaBaseCatalogParser(ABC):
    """Base parser for Tavria. Contain common methods. get_factory_objects
    method is abstract and must be implemented in child classes."""
    """TODO: Think about objects_in_db optimization."""

    _db_objects: list[BaseCatalogElement]
    _factory_objects: set[BaseCatalogElement] = set()
    _create_class: Type[BaseCatalogElement]

    def __init__(self,
                 factories: Mapping[ElType, MutableSequence[BaseFactory]],
                 db_session: Session) -> None:
        self.factories = factories
        self.db_session = db_session

    async def __call__(self) -> None:
        if MAIN_PARSER != 'Tavria':
            return
        await self.__get_db_objects()
        self._refresh_factory_table()
        await self._get_factory_objects()  # TODO: Fix name.
        await self._process_factory_objects()
        self.db_session.commit()

    async def __get_db_objects(self) -> None:
        self._db_objects = await crud.get_elements(self._create_class,
                                                   self.db_session)

    def _refresh_factory_table(self) -> None:
        """
        Instead of passing a parent_to_id table in get_objects call, we
        will make it a BaseFactory class variable and will refresh it before
        the call.
        """
        id_to_name_table = {_.id: _.name for _ in self._db_objects}
        table = {ObjectParents(
            gp_name=id_to_name_table[_.parent_id]
            if _.parent_id else None, p_name=_.name): _.id
            for _ in self._db_objects
        }
        BaseFactory.parent_table = table

    @abstractmethod
    async def _get_factory_objects(self) -> None:
        """Get objects to create from factories.
        Mustbe implemented in child classes."""

    def _mark_depricated(self, type_=ElType.PRODUCT) -> None:
        """TODO: put this code to db?"""
        to_deprecate = (_ for _ in self._db_objects
                        if _.el_type is type_
                        and _ not in self._factory_objects
                        and not _.deprecated)
        for _ in to_deprecate:
            _.deprecated = True

    def _unmark_depricated(self) -> None:
        if to_undeprecate := self._factory_objects.intersection(
            _ for _ in self._db_objects if _.deprecated
        ):
            for _ in to_undeprecate:
                _.deprecated = False

    async def _save_objects(self) -> None:
        self._factory_objects.difference_update(self._db_objects)
        if self._factory_objects:
            await crud.add_instances(self._factory_objects, self.db_session)

    async def _process_factory_objects(self) -> None:
        self._mark_depricated()
        self._unmark_depricated()
        await self._save_objects()
