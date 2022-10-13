"""SQLAlchemy database configuration."""
from abc import ABCMeta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta


SQLALCHEMY_DATABASE_URL = "sqlite:///database/database.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DeclarativeABCMeta(DeclarativeMeta, ABCMeta):
    """Mixin to allow ABC."""

Base = declarative_base(metaclass=DeclarativeABCMeta)
