"""Script to start parsing process."""
import asyncio
import cProfile  # noqa: F401
import pstats  # noqa: F401

from database import Base
from database import SessionLocal
from database import TestSession
from database import test_engine

from parsers.tavria import TAVRIA_TEST_URL  # noqa: F401
from parsers.tavria import TAVRIA_URL  # noqa: F401
from parsers.tavria import TavriaParser


session_maker = SessionLocal

test_mode = False
# test_mode = True
if test_mode:
    target_metadata = Base.metadata  # type: ignore
    target_metadata.create_all(test_engine)
    session_maker = TestSession


async def run_parser(session):
    await TavriaParser().refresh_catalog(TAVRIA_URL, session)


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
