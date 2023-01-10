"""Database constants."""
import os

from dotenv import load_dotenv


load_dotenv()


SQLALCHEMY_DATABASE_URL: str = os.environ['SQLITE_URL']
POSTGRES_DRIVER = os.environ['POSTGRES_DRIVER']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_HOST = os.environ['POSTGRES_HOST']
POSTGRES_PORT = int(os.environ['POSTGRES_PORT'])
POSTGRES_BASE_NAME = os.environ['POSTGRES_BASE_NAME']

test_mode = False
