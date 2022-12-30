"""TreeBuilder class for creating catalog tree."""
import asyncio
from collections.abc import Mapping
from typing import Iterable, MutableSequence

import aiohttp

from catalog.models import BaseCatalogElement

import crud

from project_typing import ElType

from sqlalchemy.orm import Session

from .factories import BaseFactory
from .factories import ProductFactory
from .factory_creator import FactoryCreator
from ..tavria_typing import ObjectParents
from .... import constants as c


class TreeBuilder:
    """
    Check if catalog tree exists in database
    and update it with site information.
    TODO: slots.
    """
    __factories: Mapping[ElType, MutableSequence[BaseFactory]]
    __objects_to_save: set[BaseCatalogElement] = set()

    def __call__(self, home_url: str, session: Session) -> None:
        if c.MAIN_PARSER != 'Tavria':
            return
        self.__session = session
        self.__factories = FactoryCreator(home_url)()
        self.__create_folders()
        asyncio.run(self._create_products())

    def __create_folders(self) -> None:
        for type_ in c.folder_types:
            self.__get_folders_to_save(type_)
            crud.add_instances(self.__objects_to_save,
                               self.__session)
            self.__objects_to_save.clear()
            self.__refresh_factory_table()

    def __refresh_factory_table(self) -> None:
        """
        Instead of passing a parent_to_id table in get_objects call, we
        will make it a BaseFactory class variable and will refresh it before
        the call.
        """
        saved_folders = crud.get_folders(self.__session)
        id_to_name_table = {_.id: _.name for _ in saved_folders}
        BaseFactory.parents_to_id_table = {ObjectParents(
            grand_parent_name=id_to_name_table[_.parent_id]
            if _.parent_id else None, parent_name=_.name): _.id
            for _ in saved_folders
        }

    async def _create_products(self) -> None:
        while self.__factories[ElType.PRODUCT]:
            try:
                await self.start_tasking()
            except asyncio.exceptions.TimeoutError:
                print('FINISHED', '!' * 20)
                crud.add_instances(self.__objects_to_save, self.__session)

    async def start_tasking(self):
        timeout = aiohttp.ClientTimeout(total=c.TAVRIA_SESSION_TIMEOUT_SEC)
        connector = aiohttp.TCPConnector(limit=c.TAVRIA_CONNECTIONS_LIMIT)
        async with aiohttp.ClientSession(base_url=c.TAVRIA_URL,
                                         connector=connector,
                                         timeout=timeout) as session:
            jobs = [self.one_factory_task(_, session) for _ in self.next_factories]
            await asyncio.gather(*jobs)
            raise asyncio.exceptions.TimeoutError

    def __get_folders_to_save(self, type_: ElType) -> None:
        for factory in self.__factories[type_]:
            self.__objects_to_save.update(factory.get_objects())

    async def one_factory_task(self, factory: ProductFactory, session):
        self.__objects_to_save.update(await factory.get_objects(session))
        self.__factories[ElType.PRODUCT].remove(factory)
        print('factory closed')

    @property
    def next_factories(self) -> Iterable[BaseFactory]:
        return (self.__factories[ElType.PRODUCT][_] for _ in range(c.TAVRIA_FACTORIES_PER_SESSION))\
            if len(self.__factories[ElType.PRODUCT]) >= c.TAVRIA_FACTORIES_PER_SESSION\
            else self.__factories[ElType.PRODUCT]
