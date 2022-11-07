"""Authentication constants."""
import os
from datetime import timedelta

from dotenv import load_dotenv


load_dotenv()


SECRET_KEY: str = os.environ['SECRET_KEY']
ALGORITHM: str = os.environ['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES: float\
    = float(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])
access_token_expires = timedelta(
    minutes=float(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])
)
