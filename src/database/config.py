"""SQLAlchemy database configuration.
TODO: Remove all the type ignore in code
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy import types
from sqlalchemy.orm import DeclarativeBase, sessionmaker  # type: ignore
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column  # type: ignore
from sqlalchemy.pool import StaticPool

from typing_extensions import Annotated

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
    date: types.Date(),
    Decimal: types.Numeric(),
    int: types.Integer(),
    str: types.String(),
}

int_id = Annotated[int, mapped_column(primary_key=True)]
int_fk = Annotated[int, mapped_column()]


class Base(DeclarativeBase):
    """Base model class with int id as primary key + __hash__ and __eq__."""

    id: Mapped[int_id]

    metadata = MetaData()

    __abstract__ = True
