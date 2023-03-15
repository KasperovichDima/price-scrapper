"""
Result box module for processing page results.
Provides the only one main function: 'save_results'
"""
from itertools import chain
from typing import Iterator, Sequence

from catalog.models import Product

from core.models import PriceLine

import crud

from database import int_id

from parsers.exceptions import SavingResultsException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from .support_classes import FactoryResults, ParsedProducts
from .tavria_typing import Catalog_P, FolderPath


class BoxTools:
    """
    Common tools, required for results processing:
    * retailer_id - id of current retailer.
    * sessionmaker - sessionmaker to get database session.
    * get_folder_id method.
    * configurate method.
    """
    retailer_id: int
    sessionmaker: async_sessionmaker[AsyncSession]
    __catalog: Catalog_P

    @classmethod
    def get_folder_id(cls, path: FolderPath) -> int:
        """Return id: int for specified path: Path."""
        return cls.__catalog.get_id_by_path(path)

    @classmethod
    def configurate(cls,
                    retailer_id: int,
                    sessionmaker: async_sessionmaker[AsyncSession],
                    catalog: Catalog_P) -> None:
        """Set BoxTools configuration."""

        cls.retailer_id = retailer_id
        cls.sessionmaker = sessionmaker
        cls.__catalog = catalog


async def __perform_saving(results: FactoryResults,
                           session: AsyncSession) -> None:

    # SUPPORT FUNCTIONS:
    async def get_db_products_data(
    ) -> tuple[ParsedProducts, dict[str, int_id]]:
        """Get parsed products from database from current
        folder specified by id and name to id table."""
        db_products = await crud.get_products(session,
                                              folder_ids=(folder_id,))
        return (ParsedProducts.from_products(db_products),
                {_.name: _.id for _ in db_products})
    
    async def save_new_products() -> None:
        if not (new_prod_names := results.get_new_names(parsed_products.names)):
            return
        new_products = [Product(name=name, parent_id=folder_id)
                        for name in new_prod_names]
        await crud.add_instances(new_products, session)
        await session.flush()
        nonlocal name_to_id  # type: ignore
        name_to_id.update({_.name: _.id for _ in new_products})

    async def switch_depricated() -> None:
        if to_switch := parsed_products.get_to_switch(
            results.get_page_product_ids(name_to_id)
        ):
            await crud.switch_deprecated(to_switch, session)

    async def save_new_prices() -> None:
        last_prices = await crud.get_last_prices(
            session,
            (BoxTools.retailer_id,),
            prod_ids=chain(parsed_products.depr_ids,
                           parsed_products.actual_ids)
        )
        if new_prices := get_new_prices(last_prices):
            await crud.add_instances(new_prices, session)

    def get_new_prices(last_prices: Sequence[PriceLine] | None
                       ) -> Iterator[PriceLine] | None:
        if not (page_price_tuples := tuple(results.get_price_tuples(
            BoxTools.retailer_id, name_to_id
        ))):
            return None
        existing_price_tuples = {_.as_tuple() for _ in last_prices}\
            if last_prices else tuple()
        return (PriceLine.from_tuple(tpl) for tpl in page_price_tuples
                if tpl not in existing_price_tuples)

    # MAIN FLOW:
    folder_id = BoxTools.get_folder_id(results.folder_path)
    parsed_products, name_to_id = await get_db_products_data()
    await save_new_products()
    await switch_depricated()
    await save_new_prices()


async def save_results(results: FactoryResults) -> None:
    """
    Process factory results and save them to database.
    Provides next operations:
    - SAVE NEW PRODUCTS
    - CHANGE DEPRECATED STATUS
    - SAVE NEW PRICES
    TODO: Add logging.
    """
    async with BoxTools.sessionmaker() as session:
        async with session.begin():
            try:
                await __perform_saving(results, session)
                await session.commit()
            except Exception as e:
                await session.rollback()
                msg = (
                    f'Error while saving results for\n{results.folder_path}:'
                    f'\nFailed with "{e.__class__.__name__}, {e}"'
                )
                raise SavingResultsException(msg) from e
            else:
                print(f'Successfully saved: {results.folder_path}', end='\n')
