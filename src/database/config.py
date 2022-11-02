"""SQLAlchemy database configuration."""
import os
from abc import ABCMeta

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker


load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DeclarativeABCMeta(DeclarativeMeta, ABCMeta):
    """Mixin to allow ABC."""


Base = declarative_base(metaclass=DeclarativeABCMeta)
