"""Authentication router."""
import crud

from dependencies import get_current_active_user, get_session, oauth2_scheme

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .constants import access_token_expires
from .exceptions import email_exists_exeption
from .models import User
from .schemas import TokenScheme, UserCreate, UserScheme
from .utils import authenticate_user
from .utils import create_access_token
from .utils import get_password_hash


router = APIRouter(prefix='/auth', tags=['authentication'])


@router.get("/current_user", response_model=UserScheme)
async def get_current_user(token=Depends(oauth2_scheme),
                           user: User = Depends(get_current_active_user)):
    return user


@router.post('/token', response_model=TokenScheme)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(get_session)
):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
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
                      session=Depends(get_session)):
    """Create new user and return new user's data."""
    if crud.get_user(user_data.email, session):
        raise email_exists_exeption
    user_data.password = get_password_hash(user_data.password)
    user = User(**user_data.dict())
    crud.add_instance(user, session)
    return user


@router.delete('/delete_user', response_description='email of deleted user')
async def delete_user(email: str, session=Depends(get_session)):
    """Delete user by email. If email is not in
    database - raise user_not_exists_exeption."""
    crud.delete_user(email, session)
    return email
