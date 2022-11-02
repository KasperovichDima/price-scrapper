"""Authentication validation schemas."""
from project_typing import UserType

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """UserBase validation schema."""

    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=40)
    email: str = Field(max_length=100)
    is_active: bool = Field(default=False)
    type: UserType = Field(default=UserType.USER)


class User(UserBase):
    """User validation schema."""

    id: int = Field(gt=0)
