"""
SQLAlchemy database configuration.
TODO: Switch to 2.0 Add Mapped to models
"""
from sqlalchemy import Column, Integer, MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import types

from . import constants as c


db_url = '{driver}://{user}:{password}@{host}:{port}/{db_name}'.format(
    driver=c.POSTGRES_DRIVER,
    user=c.POSTGRES_USER,
    password=c.POSTGRES_PASSWORD,
    host=c.POSTGRES_HOST,
    port=c.POSTGRES_PORT,
    db_name=c.POSTGRES_BASE_NAME
)

engine = create_engine(db_url)
DBSession = sessionmaker(engine)

test_engine = create_engine("sqlite://", poolclass=StaticPool,
                            connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


type_map = {
    bool: types.Boolean(),
    str: types.String(),
}


class Base(DeclarativeBase):
    """Base model class with int id as primary key + __hash__ and __eq__."""

    metadata = MetaData()

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
