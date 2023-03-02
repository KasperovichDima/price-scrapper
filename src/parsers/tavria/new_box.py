import asyncio
from collections import deque
from itertools import chain

from project_typing import PriceRecord  # TODO: we don't need it

from typing import Iterable, Iterator

from catalog.models import Product

from core.models import PriceLine

import crud

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from .tavria_typing import Catalog_P, ToSwitchStatus
from .tavria_typing import NameRetailPromo, Path


class ResultHandler:

    # __slots__ = ()

    # class variables:
    _retailer_id: int
    _catalog: Catalog_P
    _session_maker: async_sessionmaker[AsyncSession]
    # instance variables:
    _folder_id: int
    _db_session: AsyncSession
    _db_products: list[Product]

    _db_ids: list[int] = []
    _actual_ids: set[int] = set()
    _depr_ids: set[int] = set()
    _db_prod_names: set[str] = set()

    @classmethod
    def initialize(
        cls,
        retailer_id: int,
        catalog: Catalog_P,
        session_maker: async_sessionmaker[AsyncSession]
                   ) -> None:
        """Classmethod for initializing box with retailer_id, db_session and
        catalog which are required for it's work. Must be called befor any
        other operations with box."""
        cls._retailer_id = retailer_id
        cls._catalog = catalog
        cls._session_maker = session_maker

    def __init__(self, parent_path: Path) -> None:
        self._folder_id = self._catalog.get_id_by_path(parent_path)  # TODO: Move it to factory and get folder id in init
        self._records: deque[NameRetailPromo] = deque()

    def add_record(self, record: NameRetailPromo) -> None:
        self._records.append(record)

    def _get_price_lines(self) -> set[PriceRecord]:
        assert self._records
        name_to_id = self._prod_name_to_id
        return set(zip(
            (name_to_id[rec[0]] for rec in self._records),  # FIXME
            (self._retailer_id for _ in self._records),
            (rec[1] for rec in self._records),
            (rec[2] for rec in self._records),
            strict=True
        ))
    
    async def update(self) -> None:
        """"""
        async with self._session_maker() as self._db_session:
            async with self._db_session.begin():

                self._db_products = await crud.get_products(
                    self._db_session, folder_ids=(self._folder_id,)
                )

                await self._update_products()
                await self._update_price_lines()
                ####
                # prods = await crud.get_products(self._db_session)
                # ids = (_.id for _ in prods)
                # lines = await crud.get_last_price_lines(
                #     ids, 1, self._db_session
                # )
                ####
                await self._db_session.commit()

    async def _update_products(self) -> None:
        self._collect_db_products_data()

        if new_products := self._get_new_products():
            await crud.add_instances(new_products, self._db_session)
            self._db_products.extend(new_products)

        await crud.switch_deprecated(self._get_ids_to_switch(),
                                     self._db_session)

    def _collect_db_products_data(self) -> None:
        for product in self._db_products:
            self._db_prod_names.add(product.name)
            self._depr_ids.add(product.id)\
                if product.deprecated\
                else self._actual_ids.add(product.id)

    @property
    def _new_prod_names(self) -> Iterator[str]:
        return (rec[0] for rec in self._records
                if rec[0] not in self._db_prod_names)

    def _get_new_products(self) -> list[Product]:
        return [Product(name=name, parent_id=self._folder_id)
                for name in self._new_prod_names]

    def _get_ids_to_switch(self) -> ToSwitchStatus:
        # TODO: Optimization needed
        name_to_id = self._prod_name_to_id
        page_ids = [name_to_id[rec[0]] for rec in self._records]
        self._actual_ids.difference_update(page_ids)
        self._depr_ids.intersection_update(page_ids)
        return ToSwitchStatus(cls_=Product,
                              ids_to_depr=self._actual_ids,
                              ids_to_undepr=self._depr_ids)

    async def _update_price_lines(self) -> None:
        if new_lines := await self._get_new_lines():
            await crud.add_instances(new_lines, self._db_session)

    async def _get_new_lines(self) -> Iterable[PriceLine] | None:
        page_price_lines = self._get_price_lines()
        page_price_lines.difference_update(await self._get_last_db_lines())
        return [PriceLine.from_tuple(_) for _ in page_price_lines]

    @property
    def _prod_name_to_id(self) -> dict[str, int]:
        #  FIXME: Not tested yet.
        return {product.name: product.id for product in self._db_products}

    async def _get_last_db_lines(self) -> list[PriceLine]:
        return await crud.get_last_price_lines(
            chain(self._depr_ids, self._actual_ids),
            self._retailer_id,
            self._db_session
        )
