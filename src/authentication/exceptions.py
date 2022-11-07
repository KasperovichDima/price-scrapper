"""Authentication exceptions."""
from fastapi import HTTPException, status


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

email_exists_exeption = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Email already exists.'
)