"""Script to start parsing process."""
import asyncio
import time

from core.constants import TAVRIA_URL  # noqa: F401
from core.parsers import TavriaParser as TavriaTreeBuilder

from database import Base
from database import SessionLocal
from database import TestSession
from database import test_engine

from tests.constants import TAVRIA_TEST_URL  # noqa: F401

session_maker = SessionLocal

test_mode = False
# test_mode = True
if test_mode:
    target_metadata = Base.metadata  # type: ignore
    target_metadata.create_all(test_engine)
    session_maker = TestSession


async def run_parser(session):
    now = time.perf_counter()
    await TavriaTreeBuilder().create_catalog(TAVRIA_URL, session)
    # await TavriaTreeBuilder().create_catalog(TAVRIA_TEST_URL, session)
    print(time.perf_counter() - now)


with session_maker() as session:
    asyncio.run(run_parser(session))
