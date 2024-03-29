"""Exceptions for CRUD operations."""
from fastapi import HTTPException, status


email_exists_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Email already exists.'
)

instance_not_exists_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Instance with this params not exists.'
)
