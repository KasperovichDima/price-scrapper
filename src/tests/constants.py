"""Test constants."""
import os

from dotenv import load_dotenv


load_dotenv()


ADD_REQUEST_URL = '/report/add_request_data'
REMOVE_REQUEST_URL = '/report/remove_request_data'
GET_REPORT_URL = '/report/get_report'
TAVRIA_TEST_URL = os.environ['TAVRIA_TEST_URL']
