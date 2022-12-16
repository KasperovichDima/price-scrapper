"""Script to start parsing process."""
from core.constants import TAVRIA_URL
from core.parsers import TreeBuilder as TavriaTreeBuilder
from core.parsers import TavriaParser

from database import SessionLocal


with SessionLocal() as session:
    TavriaTreeBuilder(TAVRIA_URL, session)

# TavriaParser(TAVRIA_URL)
