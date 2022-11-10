"""Report models."""
from __future__ import annotations

from database import Base

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ReportHeader(Base):
    """
    ReportHeader class. Contain report
    meta-data. Holds a link to it's content.
    """

    __tablename__ = 'report_header'

    id = Column(Integer, primary_key=True, index=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String(100), index=True)
    note = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))

    content = relationship('ReportLine', back_populates='header')


class ReportLine(Base):
    """ReportLine class. Represents a single report data line."""

    __tablename__ = 'report_line'

    id = Column(Integer, primary_key=True, index=True)
    header_id = Column(ForeignKey('report_header.id'))
    product_id = Column(ForeignKey('product.id'))
    retailer_id = Column(ForeignKey('retailer.id'))
    retail_price = Column(Float)
    promo_price = Column(Float)

    header = relationship('ReportHeader', back_populates='content')
    product = relationship('Product')
    retailer = relationship('Retailer')