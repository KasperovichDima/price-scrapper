"""SQLAlchemy database configuration."""
from abc import ABCMeta

from constants import SQLALCHEMY_DATABASE_URL
from constants import TEST_DATABASE_URL

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


class DeclarativeABCMeta(DeclarativeMeta, ABCMeta):
    """Mixin to allow ABC."""


Base = declarative_base(metaclass=DeclarativeABCMeta)
