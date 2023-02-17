"""Tavria parser constants."""
import os
from typing import Final

from dotenv import load_dotenv


load_dotenv()


TAVRIA_URL: Final = os.environ['TAVRIA_URL']
TAVRIA_CONNECTIONS_LIMIT: Final = int(os.environ['TAVRIA_CONNECTIONS_LIMIT'])
TAVRIA_FACTORIES_PER_SESSION: Final = int(os.environ['TAVRIA_FACTORIES_PER_SESSION'])
TAVRIA_SESSION_TIMEOUT_SEC: Final = int(os.environ['TAVRIA_SESSION_TIMEOUT_SEC'])
