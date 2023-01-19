from collections.abc import Mapping
from typing import MutableSequence, Type

from catalog.models import BaseCatalogElement

import crud

from parsers.constants import MAIN_PARSER

from project_typing import ElType

from sqlalchemy.orm import Session

from .factory import BaseFactory
from .factory_creator import FactoryCreator
from .tavria_typing import ObjectParents


class TavriaBaseCatalogParser:

    factory_creator: FactoryCreator
    db_session: Session
    factories: Mapping[ElType, MutableSequence[BaseFactory]]
    type: ElType
    objects_in_db: set[BaseCatalogElement]
    factory_objects: set[BaseCatalogElement] = set()
    deprecated: set[BaseCatalogElement] = set()
    create_class: Type[BaseCatalogElement]

    async def __call__(self, db_session: Session) -> None:
        if MAIN_PARSER != 'Tavria':
            return
        self.db_session = db_session
        await self.get_db_objects()
        self.refresh_factory_table()
        await self.get_factory_objects()  # TODO: Fix name.
        await self.post_create_tasks()

    @classmethod
    def set_factories(cls, factories):
        cls.factories = factories

    async def get_db_objects(self):
        self.objects_in_db = set(await crud.get_elements(self.create_class,
                                                         self.db_session))

    def refresh_factory_table(self) -> None:
        """
        Instead of passing a parent_to_id table in get_objects call, we
        will make it a BaseFactory class variable and will refresh it before
        the call.
        """
        id_to_name_table = {_.id: _.name for _ in self.objects_in_db}
        table = {ObjectParents(
            grand_parent_name=id_to_name_table[_.parent_id]
            if _.parent_id else None, parent_name=_.name): _.id
            for _ in self.objects_in_db
        }
        BaseFactory.refresh_parent_table(table)

    def get_factory_objects(self): ...

    def mark_depricated(self, type_=ElType.PRODUCT):
        """TODO: put this code to db?"""
        to_deprecate = (_ for _ in self.objects_in_db - self.factory_objects
                        if not _.deprecated and _.el_type is type_)
        for _ in to_deprecate:
            _.deprecated = True

    def unmark_depricated(self):
        if to_undeprecate := self.factory_objects.intersection(
            _ for _ in self.objects_in_db if _.deprecated
        ):
            for _ in to_undeprecate:
                _.deprecated = False

    async def save_objects(self):
        self.factory_objects.difference_update(self.objects_in_db)
        if self.factory_objects:
            await crud.add_instances(self.factory_objects, self.db_session)
            self.objects_in_db.update(self.factory_objects)  # TODO: Think about it.

    async def post_create_tasks(self):
        self.mark_depricated()
        self.unmark_depricated()
        await self.save_objects()
