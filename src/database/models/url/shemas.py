"""URL validation schemas."""
from pydantic import BaseModel, Field


class WebPageBase(BaseModel):
    """WebPageBase validation schema."""

    product_id: int = Field(gt=0)
    retailer_id: int = Field(gt=0)
    url_id: int = Field(gt=0)


class WebPageScheme(WebPageBase):
    """WebPage validation schema."""

    id: int = Field(gt=0)


class URLBase(BaseModel):
    """URLBase validation schema."""

    url: str = Field(max_length=250)


class URLScheme(URLBase):
    """URLBase validation schema."""

    id: int = Field(gt=0)
