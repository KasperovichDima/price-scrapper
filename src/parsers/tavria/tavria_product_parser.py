import asyncio

from catalog.models import Product

from project_typing import ElType

from . import TavriaBaseCatalogParser
from . import constants as c
from . import utils as u
from .factory import ProductFactory


class TavriaProductParser(TavriaBaseCatalogParser):

    create_class = Product

    def refresh_factory_table(self) -> None:
        """Factory tables are allready refreshed after folder parser."""

    async def get_factory_objects(self):
        while self.factories[ElType.PRODUCT]:
            self.get_next_batch()
            async with u.aiohttp_session_maker() as aio_session:
                tasks = (self.single_factory_task(factory, aio_session)
                         for factory in self.factory_batch)
                try:
                    await asyncio.gather(*tasks)
                    u.tasks_are_finished()
                except asyncio.exceptions.TimeoutError:
                    if self.factory_batch:
                        self.factories[ElType.PRODUCT].extend(self.factory_batch)

    def get_next_batch(self):
        self.factory_batch = set(self.factories[ElType.PRODUCT].pop()
                                 for _ in range(self.batch_size))

    @property
    def batch_size(self) -> int:
        return c.TAVRIA_FACTORIES_PER_SESSION\
            if c.TAVRIA_FACTORIES_PER_SESSION\
            <= len(self.factories[ElType.PRODUCT])\
            else len(self.factories[ElType.PRODUCT])

    async def single_factory_task(self, factory: ProductFactory, aio_session):
        self.factory_objects.update(await factory.get_objects(aio_session))
        self.factory_batch.remove(factory)
