"""Project constants."""
import os

from dotenv import load_dotenv


load_dotenv()


SQLALCHEMY_DATABASE_URL: str = os.environ['DATABASE_URL']

CATALOG_NAMES = frozenset('Subgroup Product'.split())
RETAILER_NAMES = frozenset('Tavria Silpo Epicentr'.split())
