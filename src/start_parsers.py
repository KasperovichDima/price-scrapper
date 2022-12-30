"""Script to start parsing process."""
from core.constants import TAVRIA_URL  # noqa: F401
from core.parsers import TreeBuilder as TavriaTreeBuilder

from database import Base
from database import SessionLocal
from database import TestSession
from database import test_engine

from tests.constants import TAVRIA_TEST_URL  # noqa: F401

session_maker = SessionLocal
test_mode = True

if test_mode:
    target_metadata = Base.metadata  # type: ignore
    target_metadata.create_all(test_engine)
    session_maker = TestSession


with session_maker() as session:
    TavriaTreeBuilder()(TAVRIA_URL, session)
    # TavriaTreeBuilder()(TAVRIA_TEST_URL, session)
