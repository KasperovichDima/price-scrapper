"""Product box class."""
from typing import Iterable

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

    _group_products: list[Product]
    _db_session: Session

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
        self._group_products = await crud.get_products(
            self._db_session, folder_ids=(self._folder_id,)
        )
        await self._update_products()
        await self._update_price_lines()

    @property
    def _folder_id(self) -> int:
        assert self._factory_results.parents
        return catalog.get_id_by_path(self._factory_results.parents)

    async def _update_products(self) -> None:
        # FIXME: Long method.
        actual_prod_names: set[str] = set()
        deprecated_prod_names: set[str] = set()
        for product in self._group_products:
            if product.deprecated:
                deprecated_prod_names.add(product.name)
            else:
                actual_prod_names.add(product.name)

        page_names = {_[0] for _ in self._factory_results.records}

        if new_names := page_names - actual_prod_names - deprecated_prod_names:
            new_objects = [Product(name=name, parent_id=self._folder_id)
                           for name in new_names]
            await crud.add_instances(new_objects, self._db_session)
            self._group_products.extend(new_objects)

        # TODO: Remove redundant sets
        to_deprecate = actual_prod_names - page_names
        to_undeprecate = deprecated_prod_names & page_names
        to_switch_depr_names = to_deprecate.union(to_undeprecate)
        to_switch_depr_objects = (_ for _ in self._group_products
                                  if _.name in to_switch_depr_names)
        await crud.switch_deprecated(to_switch_depr_objects, self._db_session)

    async def _update_price_lines(self) -> None:
        if new_records := await self._get_unique_records():
            await crud.add_instances(new_records, self._db_session)

    async def _get_unique_records(self) -> Iterable[PriceLine] | None:
        """TODO: Simplifie it after debuging"""
        page_records = set(
            self._factory_results.get_price_records(self._prod_name_to_id)
        )
        db_records = await self._last_price_lines
        page_records.difference_update(db_records)
        return (PriceLine.from_tuple(rec) for rec in page_records)\
            if page_records else None

    @property
    def _prod_name_to_id(self) -> dict[str, int]:
        return {_.name: _.id for _ in self._group_products}

    @property
    async def _last_price_lines(self) -> list[PriceLine]:
        prod_ids = (_.id for _ in self._group_products)
        return await crud.get_last_price_lines(
            prod_ids, self._factory_results.retailer_id, self._db_session
        )


product_box = ProductBox()
