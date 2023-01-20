import asyncio
from collections.abc import Mapping
from typing import MutableSequence

from parsers.constants import MAIN_PARSER

from project_typing import ElType

from sqlalchemy.orm import Session

from .new_factory import Factory
from . import new_utils as u
from . import constants as c


class TavriaParser:

    _factory_batch: set[Factory]

    def __init__(self,
                 factories: Mapping[ElType, MutableSequence[Factory]],
                 db_session: Session) -> None:
        self.factories = factories
        self.db_session = db_session

    async def refresh_folders(self) -> None:
        if MAIN_PARSER != 'Tavria':
            return
        for type_ in (_ for _ in ElType if _ is not ElType.PRODUCT):
            for factory in self.factories[type_]:
                await factory(db_session=self.db_session)

    async def refresh_products(self) -> None:
        if MAIN_PARSER != 'Tavria':
            return
        while self.factories[ElType.PRODUCT]:
            self._get_next_batch()
            async with u.aiohttp_session_maker() as aio_session:
                tasks = (self.single_factory_task(factory, aio_session)
                         for factory in self._factory_batch)
                await self.__complete_tasks(tasks)

    def _get_next_batch(self) -> None:
        self._factory_batch = set(self.factories[ElType.PRODUCT].pop()
                                 for _ in range(self.batch_size))

    @property
    def batch_size(self) -> int:
        return c.TAVRIA_FACTORIES_PER_SESSION\
            if c.TAVRIA_FACTORIES_PER_SESSION\
            <= len(self.factories[ElType.PRODUCT])\
            else len(self.factories[ElType.PRODUCT])

    async def single_factory_task(self, factory: Factory,
                                  aio_session) -> None:
        await factory(aio_session=aio_session)
        self._factory_batch.remove(factory)

    async def __complete_tasks(self, tasks) -> None:
        try:
            await asyncio.gather(*tasks)
            u.tasks_are_finished()
        except asyncio.exceptions.TimeoutError:
            if self._factory_batch:
                self.factories[ElType.PRODUCT].extend(self._factory_batch)
