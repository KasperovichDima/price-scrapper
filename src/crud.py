"""
Database crud operations.
TODO: Switch to async.
"""
from typing import Iterable, Sequence

from authentication.models import User

from catalog.models import BaseCatalogElement, Folder, Product
from catalog.schemas import FolderContent

from core.models import PriceLine

import crud_exceptions as c_ex

from database import Base

from project_typing import db_type

from retailer.models import Retailer
from retailer.retailer_typing import RetailerName

from sqlalchemy import delete, select
from sqlalchemy.orm import Session


async def add_instance(instance: Base, session: Session) -> None:
    """Add new instance to database."""
    session.add(instance)
    session.commit()


async def add_instances(instances: Iterable[Base],
                        session: Session) -> None:
    """Add new instances to database."""
    session.add_all(instances)
    session.commit()


async def get_user(email: str, session: Session) -> User | None:
    """Get user instance by email."""
    stm = select(User).where(User.email == email)
    return session.execute(stm).scalar()


async def get_elements(cls_: type[db_type], session: Session,
                       **params) -> Sequence[db_type]:
    """Returns elements of specified class using
    IN statement. NOTE: kwargs dict keys must be
    named exactly like class attributes."""
    stm = select(cls_)
    for param_name, seq in params.items():
        if seq:
            stm = stm.where(getattr(cls_, param_name).in_(seq))
    return session.scalars(stm).all()


async def get_folder_content(id: int, session: Session) -> FolderContent:
    """Get content of folder with specified id."""
    return FolderContent(
        products=await get_elements(Product, session, parent_id=(id,)),
        folders=await get_elements(Folder, session, parent_id=(id,))
    )


async def get_products(
    session: Session,
    prod_ids: Iterable[int] | None = None,
    prod_names: Iterable[str] | None = None,
    folder_ids: Iterable[int] | None = None
) -> Sequence[Product]:
    """Get product objects from product and folder ids."""

    return await get_elements(Product, session, id=prod_ids,
                              name=prod_names, parent_id=folder_ids)


async def get_folders(session: Session,
                      ids: Iterable[int] | None = None,
                      ) -> Sequence[Folder]:
    """
    Get folder objects by specified parameters. If no
    ids are specified - all folders wil be returned.
    """
    return await get_elements(Folder, session, id=ids)


async def get_retailers(ids: list[int],
                        session: Session) -> Sequence[Retailer]:
    """Get retailer objects by retailer id."""
    return await get_elements(Retailer, session, id=ids)


async def delete_cls_instances(instances: Sequence[Base],
                               session: Session) -> None:
    """
    Remove specified objects from database.
    NOTE: All objects must be the same class.
    Raises same_type_exception if not.
    """

    cls_ = type(instances[0])
    if not all((isinstance(_, cls_) for _ in instances)):
        raise c_ex.same_type_exception

    session.execute(delete(cls_).where(cls_.id.in_((_.id for _ in instances))))
    session.commit()


async def delete_user(email: str, session: Session) -> None:
    """Delete user, specified by email. Raises
    user_not_exists_exception if email not in database."""
    if not (user := await get_user(email, session)):
        raise c_ex.instance_not_exists_exception
    session.delete(user)
    session.commit()


async def delete_folder(id: int, session: Session) -> int:
    """Recursively deletes folder specified by id and child folders. Also
    deletes products by CASCADE. Raises instance_not_exists_exception if
    specified folder not exists.
    
    TODO: Must be changed to only use maximum 2 queries:
          1 for folders 1 for products."""
    if not (del_folders := await get_elements(Folder, session, id=(id,))):
        raise c_ex.instance_not_exists_exception
    parent_ids = [id]
    while childs := await get_elements(Folder, session,
                                       parent_id=parent_ids):
        del_folders.extend(childs)
        parent_ids.clear()
        parent_ids.extend((_.id for _ in childs))
        childs.clear()
        childs.extend(await get_elements(Folder, session,
                                         parent_id=parent_ids))
    await delete_cls_instances(del_folders, session)
    return id


async def get_price_lines(session: Session) -> list[PriceLine]:
    return session.query(PriceLine).all()


async def get_last_price_lines(product_ids: Iterable[int],
                               reatiler_id: int,
                               session: Session) -> Sequence[PriceLine]:
    """Get last price lines for products, specified by
    product_ids, in retailer, specified by reatiler_id."""
    return session.query(PriceLine).distinct(PriceLine.product_id)\
        .order_by(PriceLine.product_id, PriceLine.date_created.desc())\
        .where(PriceLine.retailer_id.in_((reatiler_id,)),
                PriceLine.product_id.in_(product_ids)).all()


async def get_ratailer(retailer_name: RetailerName,
                       session: Session) -> Retailer:
    """Get retailer by retailer name."""
    stm = select(Retailer).where(Retailer.name == retailer_name)
    return session.execute(stm).scalar()


async def switch_deprecated(objects: Iterable[BaseCatalogElement],
                            session: Session) -> None:
    """Invert and save deprecated status."""
    for obj in objects:
        obj.deprecated = not obj.deprecated
    session.commit()
