"""Core constants."""
import os

from dotenv import load_dotenv


load_dotenv()


MAIN_PARSER = os.environ['MAIN_PARSER']

TAVRIA_URL = os.environ['TAVRIA_URL']
