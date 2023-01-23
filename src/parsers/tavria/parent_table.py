"""ParentTable class."""
import crud

from sqlalchemy.orm import Session

from .tavria_typing import ObjectParents


class ParentTable:
    """Class to refresh and get parent table.
    In this table you can find id of parent
    using parent and/or grandparent names."""

    parent_table: dict[ObjectParents, int]

    @classmethod
    async def refresh_table(cls, db_session: Session) -> None:
        folders = await crud.get_folders(db_session)
        id_to_name_table = {_.id: _.name for _ in folders}
        cls.parent_table = {ObjectParents(
            grand_parent_name=id_to_name_table[_.parent_id]
            if _.parent_id else None, parent_name=_.name): _.id
            for _ in folders}
