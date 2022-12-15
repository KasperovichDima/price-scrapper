"""Script to start parsing process."""
from core.constants import TAVRIA_URL
from core.parsers import TavriaParser


TavriaParser(TAVRIA_URL)
