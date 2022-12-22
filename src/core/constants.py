"""Core constants."""
import os

from dotenv import load_dotenv

from project_typing import ElType


load_dotenv()


MAIN_PARSER = os.environ['MAIN_PARSER']

TAVRIA_URL = os.environ['TAVRIA_URL']

folder_types = (ElType.CATEGORY, ElType.SUBCATEGORY, ElType.GROUP)
