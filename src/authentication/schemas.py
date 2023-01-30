"""Authentication validation schemas."""
from project_typing import UserType

from pydantic import BaseModel, EmailStr, Field

from . import extra_schemas as es


class UserBase(BaseModel):
    """UserBase validation schema."""

    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=40)
    email: EmailStr

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    """UserCreate validation schema."""

    password: str = Field(max_length=50)

    class Config:
        schema_extra = es.user_create


class UserScheme(UserBase):
    """User validation schema."""

    id: int = Field(gt=0)
    is_active: bool
    type: UserType

    class Config:
        schema_extra = es.user_scheme


class TokenScheme(BaseModel):
    """Token validation schema."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """TokenData validation schema."""

    username: str | None = None
