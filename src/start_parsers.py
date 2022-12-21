"""Script to start parsing process."""
from core.constants import TAVRIA_URL
from tests.constants import TAVRIA_TEST_URL
from core.parsers import TreeBuilder as TavriaTreeBuilder
from core.parsers import TavriaParser

from database import SessionLocal
from database import TestSession
from database import Base
from database import test_engine

session_type = SessionLocal
test_mode = False

if test_mode:
    target_metadata = Base.metadata  # type: ignore
    target_metadata.create_all(test_engine)
    session_type = TestSession


with session_type() as session:
    # TavriaTreeBuilder(TAVRIA_URL, session)
    TavriaTreeBuilder()(TAVRIA_TEST_URL, session)

# TavriaParser(TAVRIA_URL)
