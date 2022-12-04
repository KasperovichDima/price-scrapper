"""Product catalog validation schemas."""
from pydantic import BaseModel


class ElementScheme(BaseModel):
    """Validation scheme for content of catalog element."""

    id: int
    name: str

    class Config:
        orm_mode = True


class ElementsScheme(BaseModel):
    """GetElement validation scheme to be used in get_content function."""

    model: str | None = None
    content: list[ElementScheme] | None = None
