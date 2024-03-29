"""Script to start parsing process."""
import asyncio
import cProfile  # noqa: F401
import pstats  # noqa: F401
from time import perf_counter

import crud

from database import Base
from database import DBSession
from database import TestSession
from database import test_engine

from parsers.tavria import BoxTools
from parsers.tavria import TavriaParser
from parsers.tavria import catalog
# from parsers.tavria import product_box

from retailer.retailer_typing import RetailerName


# session_maker = DBSession

# test_mode = False
# test_mode = True
# if test_mode:
#     target_metadata = Base.metadata
#     target_metadata.create_all(test_engine)
#     session_maker = TestSession


async def run_parser():
    async with DBSession() as session:
        retailer = await crud.get_ratailer(RetailerName.TAVRIA, session)
    await catalog.initialize(retailer.home_url, DBSession)
    parser = TavriaParser(catalog, retailer.home_url)

    t0 = perf_counter()

    await parser.update_catalog()
    BoxTools.configurate(retailer.id, DBSession, catalog)
    await parser.update_products()

    print('time elapsed:', perf_counter() - t0)


if __name__ == '__main__':
    # profiler = cProfile.Profile()
    # profiler.enable()
    asyncio.run(run_parser())
    # main()
    # profiler.disable()
    # stats = pstats.Stats(profiler).sort_stats('cumtime')
    # stats.print_stats()
