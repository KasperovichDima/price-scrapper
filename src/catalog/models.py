"""Product catalog models and get model function."""
from decimal import Decimal

from database import Base, int_fk

from exceptions import EqCompareError

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column  # type: ignore


class BaseCatalogElement(Base):

    __abstract__ = True

    name: Mapped[str]
    parent_id: Mapped[int_fk] | None
    deprecated: Mapped[bool] = mapped_column(default=False)

    def __hash__(self) -> int:
        return hash((self.name, self.parent_id))

    def __eq__(self, __o: object) -> bool:
        try:
            return all((self.name == __o.name,  # type: ignore
                        self.parent_id == __o.parent_id))  # type: ignore
        except AttributeError:
            raise EqCompareError(self, __o)

    def __repr__(self) -> str:
        return self.name


class Product(BaseCatalogElement):
    """
    Product class.
    NOTE: unique in product name was removed after finding duplicate
    names on site. But on my opinion this option is required.
    """

    __tablename__ = "product"

    name: Mapped[str] = mapped_column(String(150))
    parent_id: Mapped[int_fk] = mapped_column(ForeignKey('folder.id',
                                                         ondelete='CASCADE'))
    prime_cost: Mapped[Decimal] = mapped_column(Numeric(scale=2),
                                                nullable=True)


class Folder(BaseCatalogElement):
    """Product folder class."""

    __tablename__ = 'folder'

    name: Mapped[str] = mapped_column(String(100), index=True)
    parent_id: Mapped[int] = mapped_column(index=True, nullable=True)
