"""Project constants."""
import os

from dotenv import load_dotenv


load_dotenv()


SQLALCHEMY_DATABASE_URL: str = os.environ['DATABASE_URL']

CATALOG_NAMES = frozenset(os.environ['CATALOG_NAMES'].split())
RETAILER_NAMES = frozenset(os.environ['RETAILER_NAMES'].split())
