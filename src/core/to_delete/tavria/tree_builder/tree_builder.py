"""
TreeBuilder class for creating catalog tree.
LAST RESULT: 11.36
TODO: -Take home_url from base
      -Change file name
      -Refactoring
"""
import asyncio
from collections.abc import Mapping
from typing import Iterable, MutableSequence

from catalog.models import BaseCatalogElement

import crud

from project_typing import ElType

from sqlalchemy.orm import Session

from .factories import BaseFactory
from .factories import ProductFactory
from .factory_creator import FactoryCreator
from .utils import aiohttp_session_maker
from .utils import tasks_are_finished
from ..tavria_typing import ObjectParents
from .... import constants as c


class TavriaParser:
    """Check if catalog tree exists in database
    and update it with site information."""

    __factories: Mapping[ElType, MutableSequence[BaseFactory]]
    __saved_objects: set[BaseCatalogElement]
    __objects_to_save: set[BaseCatalogElement] = set()
    __deprecated: set[BaseCatalogElement] = set()

    def __init__(self, factory_creator: FactoryCreator) -> None:
        self.__factory_creator = factory_creator

    async def refresh_catalog(self, session: Session) -> None:
        """Collect all folders and products from site and save same structure
        to database. All new objects will be saved, existing will stay
        untouched, redundant will be marked as 'deprecated'."""

        if c.MAIN_PARSER != 'Tavria':
            return
        self.__session = session
        self.__factories = self.__factory_creator()
        await self.__refresh_folders()
        print('Folders refreshed...')
        await self.__refresh_products()
        print('Products refreshed...')

    async def __refresh_folders(self) -> None:
        await self.__refresh_saved_folders()
        for type_ in c.folder_types:
            self.__grab_folders(type_)
            self.__add_deprecated(type_)
            self.__objects_to_save.difference_update(self.__saved_objects)
            await self.__save_new_folders()
            await self.__refresh_saved_folders()
            await self.__refresh_factory_table()
        if self.__deprecated:
            self.__mark_depricated()
            self.__unmark_deprecated()
            self.__session.commit()
            self.__deprecated.clear()

    def __add_deprecated(self, type_) -> None:
        deprecated = set((_ for _ in self.__saved_objects
                          if _.el_type == type_))
        deprecated.difference_update(self.__objects_to_save)
        self.__deprecated.update(deprecated)

    async def __refresh_saved_folders(self) -> None:
        self.__saved_objects = set(await crud.get_folders(self.__session))

    def __grab_folders(self, type_: ElType) -> None:
        for factory in self.__factories[type_]:
            self.__objects_to_save.update(factory.get_objects())

    async def __save_new_folders(self) -> None:
        if not self.__objects_to_save:
            return
        await crud.add_instances(self.__objects_to_save,
                                 self.__session)
        self.__objects_to_save.clear()

    def __mark_depricated(self) -> None:
        if to_mark := [_ for _ in self.__deprecated if not _.deprecated]:
            for _ in to_mark:
                _.deprecated = True

    def __unmark_deprecated(self) -> None:
        self.__saved_objects.difference_update(self.__deprecated)
        if to_unmark := [_ for _ in self.__saved_objects
                         if _.deprecated]:
            for _ in to_unmark:
                _.deprecated = False

    async def __refresh_factory_table(self) -> None:
        """
        Instead of passing a parent_to_id table in get_objects call, we
        will make it a BaseFactory class variable and will refresh it before
        the call.
        """
        id_to_name_table = {_.id: _.name for _ in self.__saved_objects}
        table = {ObjectParents(
            grand_parent_name=id_to_name_table[_.parent_id]
            if _.parent_id else None, parent_name=_.name): _.id
            for _ in self.__saved_objects
        }
        BaseFactory.refresh_parent_table(table)

    async def __refresh_products(self) -> None:
        """TODO: Refactoring"""
        from collections import defaultdict

        products_from_db = await crud.get_products(self.__session)
        self.__saved_objects = defaultdict(list)

        while products_from_db:
            _ = products_from_db.pop()
            self.__saved_objects[_.parent_id].append(_)

        while self.__factories[ElType.PRODUCT]:
            try:
                await self.__process_next_batch()
            except asyncio.exceptions.TimeoutError:
                print('saving batch...')
                await crud.add_instances(self.__objects_to_save,
                                         self.__session)

        self.__mark_depricated()
        self.__session.commit()

    async def __process_next_batch(self):
        async with aiohttp_session_maker() as session:
            tasks = (self.__single_factory_task(factory, session)
                     for factory in self.__next_batch)
            await asyncio.gather(*tasks)
            tasks_are_finished()

    @property
    def __next_batch(self) -> Iterable[BaseFactory]:
        return (self.__factories[ElType.PRODUCT][_]
                for _ in range(c.TAVRIA_FACTORIES_PER_SESSION))\
            if len(self.__factories[ElType.PRODUCT])\
            >= c.TAVRIA_FACTORIES_PER_SESSION\
            else self.__factories[ElType.PRODUCT]

    async def __single_factory_task(self, factory: ProductFactory,
                                    session) -> None:
        print(f'Group "{factory.group_name}" added to batch...')
        factory_objects = set(await factory.get_objects(session))
        saved_objects = set(self.__saved_objects.pop(factory._parent_id)) if factory._parent_id in self.__saved_objects else set()
        must_be_not_deprecated = saved_objects.intersection(factory_objects)
        if (to_unmark := [_ for _ in must_be_not_deprecated if _.deprecated]):
            for _ in to_unmark:
                _.deprecated = False
            self.__session.commit()        
        self.__deprecated.update(saved_objects - factory_objects)
        factory_objects.difference_update(saved_objects)
        self.__objects_to_save.update(factory_objects)
        self.__factories[ElType.PRODUCT].remove(factory)
