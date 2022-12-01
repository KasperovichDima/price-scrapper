"""URL models."""
import interfaces as i

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ...config import Base


class WebPage(Base, i.IWebPage):  # type: ignore
    """Web page in concrete retailer where,
    concrete product is represented."""

    __tablename__ = 'web_page'

    id = Column(Integer, primary_key=True, index=True)  # type: ignore
    product_id = Column(ForeignKey('product.id'))
    retailer_id = Column(ForeignKey('retailer.id'))
    url_id = Column(ForeignKey('url.id'))

    product = relationship('Product', back_populates='pages')  # type: ignore
    retailer = relationship('Retailer')  # type: ignore
    url = relationship('URL')  # type: ignore

    def __repr__(self) -> str:
        return f'{self.retailer}: {self.url}'


class URL(Base):  # type: ignore
    """URL address."""

    __tablename__ = 'url'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(250))

    def __repr__(self) -> str:
        return self.url  # type: ignore
