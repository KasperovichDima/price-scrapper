"""Project constants."""
import os

from dotenv import load_dotenv


load_dotenv()


SQLALCHEMY_DATABASE_URL: str = os.environ['DATABASE_URL']
TEST_DATABASE_URL: str = os.environ['TEST_DATABASE_URL']
