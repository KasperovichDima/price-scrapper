"""
Product box class.
TODO: Clear or del
"""
from typing import Generator, Iterable

from catalog.models import Product

from core.models import PriceLine

import crud

from sqlalchemy.orm import Session

from .catalog import catalog
from .tavria_typing import FactoryResults_P


class ProductBox:
    """Class for handle product factory results. Product names and prices.
    Factory just creates records from page data and drop them to the box.
    Use 'add' public method to add factory_results and perform them.
    Box will:
        1. Check if record is new and need to be saved.
        2. Should currently deprecated records in db be actualized.
        3. Should currently active records in db be deprecated.
    NOTE: 'initialize' method must be awaited before using the box.
    """

    _db_products: list[Product]
    _db_session: Session

    _actual_prod_names: set[str]
    _depr_prod_names: set[str]

    _prod_name_to_id: dict[str, int]

    __initialized = False

    async def initialize(self, db_session: Session) -> None:
        """Initialize box with db_session,
        which is required for it's work."""

        self._db_session = db_session
        self.__initialized = True

    async def add(self, factory_results: FactoryResults_P) -> None:
        """Add factory results to box. Data will be processed and saved."""

        assert self.__initialized
        self._factory_results = factory_results
        self._db_products = await crud.get_products(
            self._db_session, folder_ids=(self._folder_id,)
        )
        await self._update_products()
        await self._update_price_lines()

    @property
    def _folder_id(self) -> int:
        assert self._factory_results.parents
        return catalog.get_id_by_path(self._factory_results.parents)

    async def _update_products(self) -> None:
        self._collect_products_data()

        if new_products := self._get_new_products():
            await crud.add_instances(new_products, self._db_session)
            self._db_products.extend(new_products)

        if to_switch := self._get_objects_to_switch():
            await crud.switch_deprecated(to_switch, self._db_session)

    def _collect_products_data(self) -> None:
        self._actual_prod_names: set[str] = set()
        self._depr_prod_names: set[str] = set()
        self._prod_name_to_id = {}

        for product in self._db_products:
            self._depr_prod_names.add(product.name) if product.deprecated\
                else self._actual_prod_names.add(product.name)
            self._prod_name_to_id[product.name] = product.id

    @property  # FIXME
    def _page_prod_names(self) -> set[str]:
        return {_[0] for _ in self._factory_results.records}

    @property
    def _new_prod_names(self) -> set[str]:
        return (self._page_prod_names
                - self._actual_prod_names
                - self._depr_prod_names)

    def _get_new_products(self) -> list[Product]:
        return [Product(name=name, parent_id=self._folder_id)
                for name in self._new_prod_names]

    def _get_objects_to_switch(self) -> list[Product]:
        names_to_deprecate = self._actual_prod_names - self._page_prod_names
        names_to_actualize = self._depr_prod_names & self._page_prod_names
        names_to_switch = names_to_deprecate.union(names_to_actualize)
        return [product for product in self._db_products
                if product.name in names_to_switch]

    async def _update_price_lines(self) -> None:
        if new_records := await self._get_new_lines():
            await crud.add_instances(new_records, self._db_session)

    async def _get_new_lines(self) -> Iterable[PriceLine] | None:
        page_lines = self._factory_results.get_price_lines(
            self._prod_name_to_id
        )
        page_lines.difference_update(await self._get_last_db_lines())
        return (PriceLine.from_tuple(line) for line in page_lines)\
            if page_lines else None

    async def _get_last_db_lines(self) -> list[PriceLine]:
        return await crud.get_last_price_lines(
            self._product_ids,
            self._factory_results.retailer_id,
            self._db_session
        )

    @property
    def _product_ids(self) -> Generator[int, None, None]:
        return (_.id for _ in self._db_products)


product_box = ProductBox()
