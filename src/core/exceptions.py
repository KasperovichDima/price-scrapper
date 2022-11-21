"""Core exceptions."""
from fastapi import HTTPException, status


empty_request_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail='Some of request fields is empty.'
)
