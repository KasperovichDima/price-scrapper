"""
Database crud operations.
TODO: Switch to async.
"""
from typing import Iterable, Sequence

from authentication.models import User

from catalog.models import Folder, Product
from catalog.schemas import FolderContent

from core.models import PriceLine

import crud_exceptions as c_ex

from database import Base

from parsers.tavria import ToSwitchStatus

from project_typing import db_type

from retailer.models import Retailer
from retailer.retailer_typing import RetailerName

from sqlalchemy import delete, select, update, Update
from sqlalchemy.ext.asyncio import AsyncSession


async def add_instance(instance: Base, session: AsyncSession) -> None:
    """Add new instance to database."""
    session.add(instance)


async def add_instances(instances: Iterable[Base],
                        session: AsyncSession) -> None:
    """Add new instances to database."""
    session.add_all(instances)


async def get_user(email: str, session: AsyncSession) -> User | None:
    """Get user instance by email."""
    stm = select(User).where(User.email == email)
    return (await session.execute(stm)).scalar()


async def get_elements(cls_: type[db_type], session: AsyncSession,
                       **params) -> Sequence[db_type]:
    """Returns elements of specified class using
    IN statement. NOTE: kwargs dict keys must be
    named exactly like class attributes."""
    stm = select(cls_)
    for param_name, seq in params.items():
        if seq:
            stm = stm.where(getattr(cls_, param_name).in_(seq))
    return (await session.scalars(stm)).all()


async def get_folder_content(id: int, session: AsyncSession) -> FolderContent:
    """Get content of folder with specified id."""
    return FolderContent(
        products=await get_elements(Product, session, parent_id=(id,)),
        folders=await get_elements(Folder, session, parent_id=(id,))
    )


async def get_products(
    session: AsyncSession,
    prod_ids: Iterable[int] | None = None,
    prod_names: Iterable[str] | None = None,
    folder_ids: Iterable[int] | None = None
) -> Sequence[Product]:
    """Get product objects from product and folder ids."""

    return await get_elements(Product, session, id=prod_ids,
                              name=prod_names, parent_id=folder_ids)


async def get_folders(session: AsyncSession,
                      ids: Iterable[int] | None = None,
                      ) -> Sequence[Folder]:
    """
    Get folder objects by specified parameters. If no
    ids are specified - all folders wil be returned.
    """
    return await get_elements(Folder, session, id=ids)


async def get_retailers(ids: list[int],
                        session: AsyncSession) -> Sequence[Retailer]:
    """Get retailer objects by retailer id."""
    return await get_elements(Retailer, session, id=ids)


async def delete_cls_instances(instances: Sequence[Base],
                               session: AsyncSession) -> None:
    """
    Remove specified objects from database.
    NOTE: All objects must be the same class.
    """

    cls_ = type(instances[0])
    assert all((isinstance(_, cls_) for _ in instances))

    await session.execute(
        delete(cls_).where(cls_.id.in_((_.id for _ in instances)))
    )


async def delete_user(email: str, session: AsyncSession) -> None:
    """Delete user, specified by email. Raises
    user_not_exists_exception if email not in database."""
    if not (user := await get_user(email, session)):
        raise c_ex.instance_not_exists_exception
    await session.delete(user)


async def delete_folder(id: int, session: AsyncSession) -> int:
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


async def get_price_lines(*, prod_ids: Iterable[int] | None = None,
                          ret_ids: Iterable[int] | None = None,
                          session: AsyncSession) -> Sequence[PriceLine]:
    """Get price lines for specified (optional) products
    (by id) and for specified (optional) retailers (by id)."""
    return await get_elements(PriceLine, session,
                              product_id=prod_ids,
                              retailer_id=ret_ids)


async def get_last_prices(prod_ids: Iterable[int],
                          retailer_id: int,
                          session: AsyncSession) -> Sequence[PriceLine]:
    """Get last price lines for products, specified by
    product_ids, in retailer, specified by reatiler_id."""
    stm = select(PriceLine).distinct(PriceLine.product_id)\
        .order_by(PriceLine.product_id, PriceLine.date_created.desc())\
        .where(PriceLine.retailer_id.in_((retailer_id,)),
               PriceLine.product_id.in_(prod_ids))
    return (await session.scalars(stm)).all()


async def get_ratailer(retailer_name: RetailerName,
                       session: AsyncSession) -> Retailer:
    """Get retailer by retailer name."""
    stm = select(Retailer).where(Retailer.name == retailer_name)
    return (await session.execute(stm)).scalar()


async def switch_deprecated(to_switch: ToSwitchStatus,
                            session: AsyncSession) -> None:
    """
    Update deprecated status of the objects.
    TODO: Update logic here!
    TODO: Make it recurs.
    """

    def get_stm(status: bool) -> Update:
        ids = to_switch.ids_to_depr if status else to_switch.ids_to_undepr
        return (update(to_switch.cls_)
                .where(to_switch.cls_.id.in_(ids))
                .values(deprecated=status))
    
    async def execute(stms: Iterable[Update]) -> None:
        for _ in stms:
            await session.execute(_)

    await execute((get_stm(True), get_stm(False)))