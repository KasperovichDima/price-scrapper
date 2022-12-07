"""Authentication validation schemas."""
from project_typing import UserType

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """UserBase validation schema."""

    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=40)
    email: EmailStr

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    """UserCreate validation schema."""

    is_active: bool = Field(default=False)
    password: str = Field(max_length=50)
    type: UserType = Field(default=UserType.USER)


class UserScheme(UserBase):
    """User validation schema."""

    id: int = Field(gt=0)
    is_active: bool
    type: UserType


class TokenScheme(BaseModel):
    """Token validation schema."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """TokenData validation schema."""

    username: str | None = None
