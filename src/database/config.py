"""SQLAlchemy database configuration."""
from . import constants as c

from database.constants import SQLALCHEMY_DATABASE_URL

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


postgres_url = URL(
    drivername=c.POSTGRES_DRIVER,
    username=c.POSTGRES_USER,
    password=c.POSTGRES_PASSWORD,
    host=c.POSTGRES_HOST,
    port=c.POSTGRES_PORT,
    database=c.POSTGRES_BASE_NAME
)

engine = create_engine(postgres_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

test_engine = create_engine("sqlite://",
                            connect_args={"check_same_thread": False},
                            poolclass=StaticPool)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base = declarative_base(metaclass=DeclarativeMeta)
