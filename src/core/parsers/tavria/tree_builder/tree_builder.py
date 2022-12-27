"""TreeBuilder class for creating catalog tree."""
import asyncio
import aiohttp
from collections.abc import Mapping
from typing import Iterable

from catalog.models import BaseCatalogElement

import crud

from project_typing import ElType

from sqlalchemy.orm import Session

from .factories import BaseFactory
from .tag_data_preparator import FactoryCreator
from ....constants import MAIN_PARSER, folder_types
from ....constants import TAVRIA_CONNECTIONS_LIMIT
from ....core_typing import ObjectParents


class TreeBuilder:
    """
    Check if catalog tree exists in database
    and update it with site information.
    TODO: slots.
    """
    __factories: Mapping[ElType, Iterable[BaseFactory]]
    __objects_to_save: list[BaseCatalogElement] = []

    def __call__(self, home_url: str, session: Session) -> None:
        if MAIN_PARSER != 'Tavria':
            return
        self.__session = session
        self.__factories = FactoryCreator(home_url)()
        self.__create_folders()
        asyncio.run(self.__create_products())

    def __create_folders(self) -> None:
        for type_ in folder_types:
            self.__objects_to_save.clear()
            self.__refresh_factory_table()
            self.__get_folders_to_save(type_)
            crud.add_instances(self.__objects_to_save,
                               self.__session)

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

    def __get_folders_to_save(self, type_: ElType) -> None:
        for factory in self.__factories[type_]:
            self.__objects_to_save.extend(
                factory.get_objects()
            )

    async def __create_products(self) -> None:
        self.__objects_to_save.clear()
        connector = aiohttp.TCPConnector(limit=TAVRIA_CONNECTIONS_LIMIT)
        async with aiohttp.ClientSession(connector=connector) as session:
            jobs = (_.get_objects(session) for _ in self.__factories[ElType.PRODUCT])
            products = await asyncio.gather(*jobs)
            return products
