"""Script to start parsing process."""
import asyncio
import cProfile  # noqa: F401
import pstats  # noqa: F401

import crud

from database import Base
from database import DBSession
from database import TestSession
from database import test_engine

from parsers.tavria import FactoryCreator
from parsers.tavria import ProductFactory, TavriaParser
from parsers.tavria import catalog
from parsers.tavria import product_box

from retailer.retailer_typing import RetailerName


session_maker = DBSession

test_mode = False
# test_mode = True
if test_mode:
    target_metadata = Base.metadata
    target_metadata.create_all(test_engine)
    session_maker = TestSession


async def run_parser(session):
    retailer = await crud.get_ratailer(RetailerName.TAVRIA, session)
    await catalog.initialize(retailer.home_url, session)
    f_creator = FactoryCreator(retailer, ProductFactory)
    parser = TavriaParser(catalog, f_creator)
    await parser.update_catalog()
    await product_box.initialize(catalog, session)
    await parser.update_products()


def main():
    with session_maker() as session:
        asyncio.run(run_parser(session))


if __name__ == '__main__':
    # profiler = cProfile.Profile()
    # profiler.enable()
    main()
    # profiler.disable()
    # stats = pstats.Stats(profiler).sort_stats('cumtime')
    # stats.print_stats()
