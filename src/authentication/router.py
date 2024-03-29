"""Authentication router."""
import crud

from crud_exceptions import email_exists_exception

from dependencies import get_current_active_user, get_db_session, oauth2_scheme

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from .constants import access_token_expires
from .models import User
from .schemas import TokenScheme, UserCreate, UserScheme
from .utils import authenticate_user
from .utils import create_access_token
from .utils import get_password_hash


router = APIRouter(prefix='/auth', tags=['authentication'])


@router.get("/current_user",
            response_model=UserScheme,
            summary='Get current active user.')
async def get_current_user(token=Depends(oauth2_scheme),
                           user: User = Depends(get_current_active_user)):
    return user


@router.post('/token', response_model=TokenScheme)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(get_db_session)
):
    """Attempt to get access token by username and password from form data.
    Raises HTTPException if username not exiss or password is incorrect.
    Returns dict with token and token_type."""
    if not (user := await authenticate_user(form_data.username,
                                            form_data.password,
                                            session)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post('/create_user', response_model=UserScheme)
async def create_user(user_data: UserCreate,
                      session: AsyncSession = Depends(get_db_session)):
    """Creates new user and returns new user's data. If
    email already exists - raises email_exists_exception."""
    if await crud.get_user(user_data.email, session):
        raise email_exists_exception
    user_data.password = get_password_hash(user_data.password)
    user = User(**user_data.dict())
    await crud.add_instance(user, session)
    await session.commit()
    return user


@router.delete('/delete_user', response_description='email of deleted user')
async def delete_user(email: str = Body(example='john@travolta.com'),
                      session: AsyncSession = Depends(get_db_session)) -> str:
    """Deletes user by email. If email is not in
    database - raises instance_not_exists_exception."""
    await crud.delete_user(email, session)
    await session.commit()
    return email
