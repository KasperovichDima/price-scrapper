"""URL models."""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ...config import Base


class WebPage(Base):
    """Web page in concrete retailer where,
    concrete product is represented."""

    __tablename__ = 'web_page'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(ForeignKey('product.id'))
    retailer_id = Column(ForeignKey('retailer.id'))
    url_id = Column(ForeignKey('url.id'))

    product = relationship('Product', back_populates='pages')
    retailer = relationship('Retailer')
    url = relationship('URL')

    def __repr__(self) -> str:
        return self.url


class URL(Base):
    """URL address."""

    __tablename__ = 'url'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(250))

    def __repr__(self) -> str:
        return self.url
