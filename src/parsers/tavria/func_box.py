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
from collections import deque
from itertools import chain
from dataclasses import dataclass, field

from project_typing import PriceRecord  # TODO: we don't need it

from typing import Iterable, Iterator, NamedTuple, Sequence

from catalog.models import Product

from core.models import PriceLine

import crud

from database import int_id

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from .tavria_typing import Catalog_P
from .support_classes import FactoryResults, ToSwitchStatus
from .tavria_typing import NameRetailPromo, Path



class Tools:  # TODO: Name
    retailer_id: int
    sessionmaker: async_sessionmaker[AsyncSession]
    __catalog: Catalog_P

    @classmethod
    def get_folder_id(cls, path: Path) -> int:
        return cls.__catalog.get_id_by_path(path)
    
    @classmethod
    def configurate(cls,
                    retailer_id: int,
                    sessionmaker: async_sessionmaker[AsyncSession],
                    catalog: Catalog_P) -> None:
        cls.retailer_id = retailer_id
        cls.sessionmaker = sessionmaker
        cls.__catalog = catalog


@dataclass(eq=False, order=False, frozen=True, slots=True)
class DBParsed:
    names: set[str] = field(default_factory=set)
    depr_ids: set[int] = field(default_factory=set)
    actual_ids: set[int] = field(default_factory=set)


def get_db_parsed(products: Sequence[Product]) -> DBParsed:
    names: set[str] = set()
    depr: set[int] = set()
    actual: set[int] = set()
    for _ in products:
        depr.add(_.id) if _.deprecated else actual.add(_.id)
        names.add(_.name)
    return DBParsed(names, depr, actual)


def get_to_switch(db_parsed: DBParsed, page_ids: set[int]) -> ToSwitchStatus | None:
    to_depr = db_parsed.actual_ids - page_ids
    to_undepr = db_parsed.depr_ids & page_ids
    if any((to_depr, to_undepr)):
        return ToSwitchStatus(
            cls_ = Product,
            ids_to_depr=to_depr,
            ids_to_undepr=to_undepr
        )


# async def switch_deprecated(db_parsed: DBParsed, page_ids: set[int]) -> None:
#     if to_switch := get_to_switch(db_parsed, page_ids):
#         async with Tools.sessionmaker() as session:
#             await crud.switch_deprecated(to_switch, session)
#             await session.flush()

async def switch_deprecated(db_parsed: DBParsed, page_ids: set[int], session) -> None:
    if to_switch := get_to_switch(db_parsed, page_ids):
        # async with Tools.sessionmaker() as session:
        await crud.switch_deprecated(to_switch, session)
        await session.flush()


def get_price_records(
        records: deque[NameRetailPromo],
        name_to_id: dict[str, int_id]
) -> Iterator[PriceRecord]:
    return zip(
            (name_to_id[rec[0]] for rec in records),
            (Tools.retailer_id for _ in records),
            (rec[1] for rec in records),
            (rec[2] for rec in records),
            strict=True
        )


def get_new_price_lines(
        last_prices: Sequence[PriceLine],
        records: deque[NameRetailPromo],
        name_to_id: dict[str, int_id]
) -> list[PriceLine] | None:
    if not (price_records := tuple(get_price_records(records, name_to_id))):
        return None
    existing_records = {_.as_tuple() for _ in last_prices}
    return [PriceLine.from_tuple(_) for _ in price_records
            if _ not in existing_records]


async def add_results(results: FactoryResults) -> None:
    async with Tools.sessionmaker() as session:
        async with session.begin():

            print('adding data from', results.folder_path)   #DEBUG!!!
            folder_id = Tools.get_folder_id(results.folder_path)
            # async with Tools.sessionmaker() as session:
            db_products = await crud.get_products(session, folder_ids=(folder_id,))
            db_parsed = get_db_parsed(db_products)  # TODO: Naming
            last_prices = await crud.get_last_prices(
                chain(db_parsed.depr_ids, db_parsed.actual_ids),
                Tools.retailer_id,
                session
            )
            name_to_id = {_.name: _.id for _ in db_products}
            new_names: list[str] = []
            page_ids: set[int] = set()

            for record in results.records:
                name = record[0]
                if name not in db_parsed.names:
                    new_names.append(name)
                    continue
                page_ids.add(name_to_id[name])

            # print(new_names)   #DEBUG!!!

            if new_names:
                new_products = [Product(name=name, parent_id=folder_id) for name in new_names]
                # async with Tools.sessionmaker() as session:
                await crud.add_instances(new_products, session)
                new_products = await crud.get_products(session, prod_names=new_names)
                print(new_products)
                name_to_id.update({_.name: _.id for _ in new_products})  # TODO: Needed?!!!!!!!
                del new_products

            del new_names
            
            await switch_deprecated(db_parsed, page_ids, session)

            if new_price_lines := get_new_price_lines(last_prices, results.records, name_to_id):
                # async with Tools.sessionmaker() as session:
                await crud.add_instances(new_price_lines, session)
                # await session.flush()
            
            print(results.folder_path, 'FINISHED!')
            await session.commit()
