"""Database constants."""
import os
from typing import Final

from dotenv import load_dotenv


load_dotenv()


POSTGRES_DRIVER: Final = os.environ['POSTGRES_DRIVER']
POSTGRES_USER: Final = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD: Final = os.environ['POSTGRES_PASSWORD']
POSTGRES_HOST: Final = os.environ['POSTGRES_HOST']
POSTGRES_PORT: Final = int(os.environ['POSTGRES_PORT'])
POSTGRES_BASE_NAME: Final = os.environ['POSTGRES_BASE_NAME']
