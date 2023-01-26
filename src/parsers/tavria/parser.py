import asyncio
from collections.abc import Mapping
from typing import MutableSequence

from parsers.constants import MAIN_PARSER

from project_typing import ElType

from sqlalchemy.orm import Session

from . import constants as c
from . import utils as u
from .factory import BaseFactory
from .objects_box import ObjectsBox
from .parent_table import ParentTable


class TavriaParser:

    _factory_batch: set[BaseFactory]

    def __init__(self,
                 factories: Mapping[ElType, MutableSequence[BaseFactory]],
                 db_session: Session) -> None:
        self.factories = factories
        self.db_session = db_session
        self.object_box = ObjectsBox(db_session)

    async def refresh_catalog(self) -> None:
        if MAIN_PARSER != 'Tavria':
            return
        await self._refresh_folders()
        await self._refresh_products()

    async def _refresh_folders(self) -> None:
        for type_ in (_ for _ in ElType if _ is not ElType.PRODUCT):
            for factory in self.factories[type_]:
                await factory(object_box=self.object_box)
            await self.object_box.save_all()
            await ParentTable.refresh_table(self.db_session)

    async def _refresh_products(self) -> None:
        while self.factories[ElType.PRODUCT]:
            self._get_next_batch()
            async with u.aiohttp_session_maker() as aio_session:
                tasks = (self.single_factory_task(factory, aio_session)
                         for factory in self._factory_batch)
                await self.__complete_tasks(tasks)
        await self.object_box.save_all()

    def _get_next_batch(self) -> None:
        self._factory_batch = set(self.factories[ElType.PRODUCT].pop()
                                  for _ in range(self.batch_size))

    @property
    def batch_size(self) -> int:
        return c.TAVRIA_FACTORIES_PER_SESSION\
            if c.TAVRIA_FACTORIES_PER_SESSION\
            <= len(self.factories[ElType.PRODUCT])\
            else len(self.factories[ElType.PRODUCT])

    async def single_factory_task(self, factory: BaseFactory,
                                  aio_session) -> None:
        await factory(object_box=self.object_box,
                      aio_session=aio_session)
        self._factory_batch.remove(factory)

    async def __complete_tasks(self, tasks) -> None:
        try:
            await asyncio.gather(*tasks)
            u.tasks_are_finished()
        except asyncio.exceptions.TimeoutError:
            if self._factory_batch:
                self.factories[ElType.PRODUCT].extend(self._factory_batch)
