"""Tavria price parser."""
import asyncio
from typing import Coroutine, Iterator

from . import constants as c
from . import utils as u
from .factory import ProductFactory
from .tavria_typing import Catalog_P


class TavriaParser:
    """Parser for collecting data from specified retailer."""

    _catalog_urls: list[str]
    _url_batch: set[str]

    def __init__(self, catalog: Catalog_P,
                 retailer_url: str) -> None:
        self._catalog = catalog
        self._retailer_url = retailer_url

    async def update_catalog(self) -> None:
        """Update catalog folder structure in the
        database and synchronize it with webpage."""
        await self._catalog.update()

    async def update_products(self) -> None:
        """Update products in database and save actual prices."""
        self._catalog_urls = u.get_catalog_urls(self._retailer_url)

        while self._catalog_urls:
            self._get_next_batch()
            async with u.aiohttp_session_maker() as aio_session:
                tasks = (self._single_url_task(url, aio_session)
                         for url in self._url_batch)
                await self._complete_tasks(tasks)

    def _get_next_batch(self) -> None:
        self._url_batch = {self._catalog_urls.pop()
                           for _ in range(self._batch_size)}

    @property
    def _batch_size(self) -> int:
        return c.TAVRIA_FACTORIES_PER_SESSION\
            if c.TAVRIA_FACTORIES_PER_SESSION\
            <= len(self._catalog_urls)\
            else len(self._catalog_urls)

    async def _single_url_task(self, url: str, aio_session) -> None:
        await ProductFactory(url).run(aio_session)
        self._url_batch.remove(url)

    async def _complete_tasks(self, tasks: Iterator[Coroutine]) -> None:
        try:
            await asyncio.gather(*tasks)
            u.tasks_are_finished()
        except asyncio.exceptions.TimeoutError:
            if self._url_batch:
                self._catalog_urls.extend(self._url_batch)
