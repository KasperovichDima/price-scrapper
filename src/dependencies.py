"""Application dependecies."""
from authentication.constants import ALGORITHM, SECRET_KEY
from authentication.exceptions import credentials_exception
from authentication.schemas import TokenData, UserScheme

import crud

from database import DBSession
from database import TestSession

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_db_session():
    """
    Returns database connection.
    TODO: think about commented...
    """
    session = DBSession()
    try:
        yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_test_session():
    """Returns test database connection."""
    session = TestSession()
    try:
        yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_current_user(token: str = Depends(oauth2_scheme),
                           session=Depends(get_db_session)):
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
    user = await crud.get_user(token_data.username, session)
    return user


async def get_current_active_user(user: UserScheme
                                  = Depends(get_current_user)):
    """
    Return current user, if current user
    is active. Else - raise HTTPException.
    """
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
