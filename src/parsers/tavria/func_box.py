"""
- get all products of this group (by path)
- get last prices of this group
- sort their ids
- create name to id table
- check, if new products
    - SAVE NEW PRODUCTS
    - CHANGE DEPRECATED STATUS
    - update name to id table
- check, if new prices (if price is different or new price for poroduct)
- SAVE NEW PRICES

TODO: Datatype optymization.
TODO: Naming optymization.
TODO: Docstrings.
"""
from itertools import chain
from typing import Iterator, Sequence

from catalog.models import Product

from core.models import PriceLine

import crud

from database import int_id

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from .support_classes import FactoryResults, ParsedProducts
from .tavria_typing import Catalog_P, Path


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
    def get_folder_id(cls, path: Path) -> int:
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


def __get_new_prices(last_prices: Sequence[PriceLine],
                     results: FactoryResults,
                     name_to_id: dict[str, int_id]
                     ) -> Iterator[PriceLine] | None:
    if not (price_tuples := tuple(results.get_price_tuples(
        BoxTools.retailer_id, name_to_id
    ))):
        return None
    existing_price_tuples = {_.as_tuple() for _ in last_prices}
    return (PriceLine.from_tuple(_) for _ in price_tuples
            if _ not in existing_price_tuples)


async def __perform_adding(results: FactoryResults,
                           session: AsyncSession) -> None:
    folder_id = BoxTools.get_folder_id(results.folder_path)
    db_products = await crud.get_products(session,
                                          folder_ids=(folder_id,))
    parsed_products = ParsedProducts.from_products(db_products)
    name_to_id = {_.name: _.id for _ in db_products}

    del db_products

    if new_prod_names := results.get_new_names(parsed_products.names):
        new_products = [Product(name=name, parent_id=folder_id)
                        for name in new_prod_names]
        await crud.add_instances(new_products, session)
        await session.flush()
        name_to_id.update({_.name: _.id for _ in new_products})

        del new_products

    del folder_id, new_prod_names

    if to_switch := parsed_products.get_to_switch(
        results.get_page_product_ids(name_to_id)
    ):
        await crud.switch_deprecated(to_switch, session)

    last_prices = await crud.get_last_prices(
        session, (BoxTools.retailer_id,),
        prod_ids=chain(parsed_products.depr_ids, parsed_products.actual_ids)
    )
    if new_prices := __get_new_prices(last_prices,
                                      results,
                                      name_to_id):
        await crud.add_instances(new_prices, session)


async def save_results(results: FactoryResults) -> None:
    """Process factory results and save them to database."""
    async with BoxTools.sessionmaker() as session:
        async with session.begin():
            try:
                await __perform_adding(results, session)
                await session.commit()
                msg = f'Results for {results.folder_path} successfully saved!'
            except Exception as e:
                await session.rollback()
                msg = (f'Saving results for {results.folder_path}'
                       f'failed with "{e.__class__.__name__}, {e}"')
            finally:
                #  TODO: log msg
                print(msg)
