"""Application dependecies."""
from authentication.constants import ALGORITHM, SECRET_KEY
from authentication.exceptions import credentials_exception
from authentication.schemas import TokenData, UserScheme

import crud

from database import SessionLocal

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt

from sqlalchemy.orm import Session


def get_session():
    """Returns database connection."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: Session = Depends(get_session)):
    """Returns current user by token."""
    try:
        payload = jwt.decode(
            token, SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    assert token_data.username
    current_user = crud.get_user(token_data.username, db)
    return current_user


async def get_current_active_user(user: UserScheme
                                  = Depends(get_current_user)):
    """
    Return current user, if current user
    is active. Else - raise HTTPException.
    """
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
