"""ParentTable class."""
import crud

from sqlalchemy.orm import Session

from .tavria_typing import ObjectParents


class ParentTable:
    """Class to refresh and get parent table.
    In this table you can find id of parent
    using parent and/or grandparent names."""

    __parent_table: dict[ObjectParents, int]

    @classmethod
    async def refresh_table(cls, db_session: Session) -> None:
        """Refresh table after saving new data to db."""
        folders = await crud.get_folders(db_session)
        id_to_name_table = {_.id: _.name for _ in folders}
        cls.__parent_table = {ObjectParents(
            gp_name=id_to_name_table[_.parent_id]
            if _.parent_id else None, p_name=_.name): _.id
            for _ in folders}
        pass

    @classmethod
    def get_table(cls) -> dict[ObjectParents, int]:
        return cls.__parent_table
