"""Product box class."""
from typing import Iterable, Iterator

from catalog.models import Product

from core.models import PriceLine

import crud

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from .tavria_typing import Catalog_P, FactoryResults_P
from .support_classes import ToSwitchStatus


class ProductBox:
    """
    Class for handle product factory results. Product names and prices.
    Factory just creates records from page data and drop them to the box.
    Use 'add' public method to add factory_results and perform them.
    Box will:
        1. Check if record is new and need to be saved.
        2. Should currently deprecated records in db be actualized.
        3. Should currently active records in db be deprecated.
    NOTE: 'initialize' method must be awaited before using the box.
    """

    _folder_id: int
    _catalog: Catalog_P
    _session_maker: async_sessionmaker[AsyncSession]
    _db_session: AsyncSession
    _factory_results: FactoryResults_P
    _db_products: list[Product]

    _db_ids: list[int] = []
    _actual_ids: set[int] = set()
    _depr_ids: set[int] = set()
    _db_prod_names: set[str] = set()

    async def initialize(
            self, catalog: Catalog_P,
            session_maker: async_sessionmaker[AsyncSession]
    ) -> None:
        """Initialize box with db_session and
        catalog which are required for it's work."""

        self._catalog = catalog
        self._session_maker = session_maker

    async def add(self, factory_results: FactoryResults_P) -> None:
        """Add factory results to box. Data will be processed and saved."""
        assert self._session_maker

        self._folder_id = self._catalog.get_id_by_path(factory_results.parent_path)
        self._factory_results = factory_results
        async with self._session_maker() as db_session:
            async with db_session.begin():

                self._db_products = await crud.get_products(
                    db_session, folder_ids=(self._folder_id,)
                )

                self._db_session = db_session
                await self._update_products()
                await self._update_price_lines()

                await db_session.commit()

    async def _update_products(self) -> None:
        self._collect_db_products_data()

        if new_products := self._get_new_products():
            print(new_products)
            await crud.add_instances(new_products, self._db_session)
            self._db_products.extend(new_products)

        await crud.switch_deprecated(self._get_ids_to_switch(),
                                     self._db_session)

    def _collect_db_products_data(self) -> None:
        for product in self._db_products:
            self._db_prod_names.add(product.name)
            self._db_ids.append(product.id)
            self._depr_ids.add(product.id)\
                if product.deprecated\
                else self._actual_ids.add(product.id)

    @property
    def _page_prod_names(self) -> Iterator[str]:
        # print(self._factory_results.records)
        return (_[0] for _ in self._factory_results.records)
    @property
    def _new_prod_names(self) -> Iterator[str]:
        return (name for name in self._page_prod_names
                if name not in self._db_prod_names)

    def _get_new_products(self) -> list[Product]:
        return [Product(name=name, parent_id=self._folder_id)
                for name in self._new_prod_names]

    def _get_ids_to_switch(self) -> ToSwitchStatus:
        self._actual_ids.difference_update(self._db_ids)
        self._depr_ids.intersection_update(self._db_ids)
        return ToSwitchStatus(cls_=Product,
                              ids_to_depr=self._actual_ids,
                              ids_to_undepr=self._depr_ids)

    async def _update_price_lines(self) -> None:
        if new_records := await self._get_new_lines():
            await crud.add_instances(new_records, self._db_session)

    async def _get_new_lines(self) -> Iterable[PriceLine] | None:
        page_price_lines = self._factory_results.get_price_lines(
            self._prod_name_to_id
        )
        page_price_lines.difference_update(await self._get_last_db_lines())
        return (PriceLine.from_tuple(line) for line in page_price_lines)\
            if page_price_lines else None

    @property
    def _prod_name_to_id(self) -> dict[str, int]:
        #  FIXME: Not tested yet.
        return {product.name: product.id for product in self._db_products}

    async def _get_last_db_lines(self) -> list[PriceLine]:
        return await crud.get_last_prices(
            self._db_ids,
            self._factory_results.retailer_id,
            self._db_session
        )


product_box = ProductBox()
