"""Core constants."""
import os

from dotenv import load_dotenv

from project_typing import ElType


load_dotenv()


MAIN_PARSER = os.environ['MAIN_PARSER']

folder_types = (ElType.CATEGORY, ElType.SUBCATEGORY, ElType.GROUP)  # TODO: del after refactoring
