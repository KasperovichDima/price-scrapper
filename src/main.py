"""Application main."""
from authentication.constants import access_token_expires
from authentication.exceptions import email_exists_exeption
from authentication.models import User
from authentication.schemas import TokenScheme, UserCreate, UserScheme
from authentication.utils import authenticate_user
from authentication.utils import create_access_token
from authentication.utils import get_password_hash

import crud

from dependencies import get_current_active_user, get_session, oauth2_scheme

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm


app = FastAPI()


def fake_hash_password(password: str):
    return "fakehashed" + password


@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.get("/users/me", response_model=UserScheme)
async def read_users_me(user: User = Depends(get_current_active_user)):
    return user


@app.post("/token", response_model=TokenScheme)
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


@app.post('/create_user', response_model=UserScheme)
async def create_user(user_data: UserCreate,
                      session=Depends(get_session)):
    """Create new user and return new user's data."""
    if crud.get_user(user_data.email, session):
        raise email_exists_exeption
    user_data.password = get_password_hash(user_data.password)
    user = User(**user_data.dict())
    crud.add_instance(user, session)
    return user
