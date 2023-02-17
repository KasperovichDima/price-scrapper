"""Core constants."""
import os
from typing import Final

from dotenv import load_dotenv


load_dotenv()


MAIN_PARSER: Final = os.environ['MAIN_PARSER']