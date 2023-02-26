"""SQLAlchemy database configuration."""
from datetime import date
from decimal import Decimal

from sqlalchemy import MetaData
from sqlalchemy import types
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from typing_extensions import Annotated

from . import constants as c


from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine


db_url = '{driver}://{user}:{password}@{host}:{port}/{db_name}'.format(
    driver=c.POSTGRES_DRIVER,
    user=c.POSTGRES_USER,
    password=c.POSTGRES_PASSWORD,
    host=c.POSTGRES_HOST,
    port=c.POSTGRES_PORT,
    db_name=c.POSTGRES_BASE_NAME
)

engine = create_async_engine(db_url)
DBSession = async_sessionmaker(engine, expire_on_commit=False)

test_engine = create_async_engine("sqlite+aiosqlite://",
                                  connect_args={"check_same_thread": False})

TestSession = async_sessionmaker(test_engine, expire_on_commit=False)

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
