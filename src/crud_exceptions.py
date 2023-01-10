"""
Exceptions for CRUD operations.
TODO: Unite user_not_exists_exeption and instance_not_exists_exeption.
"""
from fastapi import HTTPException, status


email_exists_exeption = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Email already exists.'
)

user_not_exists_exeption = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='User with this email not exists.'
)

instance_not_exists_exeption = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Instance with this id not exists.'
)

same_type_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='All objects must be the same class.'
)