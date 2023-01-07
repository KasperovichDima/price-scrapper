"""Project constants."""
import os

from dotenv import load_dotenv


load_dotenv()


SQLALCHEMY_DATABASE_URL: str = os.environ['DATABASE_URL']

test_mode = True

ADD_REQUEST_URL = '/report/add_request_data'
REMOVE_REQUEST_URL = '/report/remove_request_data'
