"""Tavria price parser."""
import asyncio
from collections import deque
from typing import Coroutine, Iterator

from . import constants as c
from . import utils as u
from .tavria_typing import Catalog_P
from .tavria_typing import FactoryCreator_P
from .tavria_typing import Factory_P


class TavriaParser:
    """Parser for collecting data from specified retailer."""

    _factories: deque[Factory_P]

    def __init__(self, catalog: Catalog_P,
                 f_creator: FactoryCreator_P) -> None:
        self._catalog = catalog
        self._f_creator = f_creator

    async def update_catalog(self) -> None:
        """Update catalog folder structure in the
        database and synchronize it with webpage."""
        await self._catalog.update()

    async def update_products(self) -> None:
        """Update products in database and save actual prices."""
        await self._get_factories()
        while self._factories:
            self._get_next_batch()
            async with u.aiohttp_session_maker() as aio_session:
                tasks = (self._single_factory_task(factory, aio_session)
                         for factory in self._factory_batch)
                await self._complete_tasks(tasks)

    async def _get_factories(self) -> None:
        self._factories = self._f_creator.create()
        del self._f_creator

    def _get_next_batch(self) -> None:
        self._factory_batch = {self._factories.pop()
                               for _ in range(self._batch_size)}

    @property
    def _batch_size(self) -> int:
        return c.TAVRIA_FACTORIES_PER_SESSION\
            if c.TAVRIA_FACTORIES_PER_SESSION\
            <= len(self._factories)\
            else len(self._factories)

    async def _single_factory_task(self, factory: Factory_P,
                                   aio_session) -> None:
        await factory.run(aio_session)
        self._factory_batch.remove(factory)

    async def _complete_tasks(self, tasks: Iterator[Coroutine]) -> None:
        try:
            await asyncio.gather(*tasks)
            u.tasks_are_finished()
        except asyncio.exceptions.TimeoutError:
            if self._factory_batch:
                self._factories.extend(self._factory_batch)
