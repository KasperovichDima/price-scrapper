"""Authentication constants."""
import os
from datetime import timedelta
from typing import Final

from dotenv import load_dotenv


load_dotenv()


SECRET_KEY: Final = os.environ['SECRET_KEY']
ALGORITHM: Final = os.environ['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES: Final\
    = float(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])
access_token_expires: Final = timedelta(
    minutes=float(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])
)
