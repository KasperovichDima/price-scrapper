from catalog.models import Folder

import crud

from sqlalchemy.orm import Session

from .tavria_typing import Path


class FolderHashes:

    db_folders: list[Folder]
    _id_to_folder: dict[int, Folder] = {}
    _path_to_id: dict[Path, int] = {}
    _ids_with_childs: set[int]
    _deprecated_ids: set[int] = set()

    async def initialize(self, db_session: Session) -> None:
        db_folders = await crud.get_folders(db_session)
        self._ids_with_childs = {_.parent_id for _ in db_folders if _.parent_id}
        for folder in db_folders:

            if folder.parent_id and folder.parent_id not in self._ids_with_childs:
                self._ids_with_childs.add(folder.parent_id)
        
            self._id_to_folder[folder.id] = folder

            path = self._get_path(folder)
            self._path_to_id[path] = folder.id

    def _get_path(self, folder: Folder) -> Path:
        if folder.id not in self._ids_with_childs:  # GROUP
            p_name, gp_name = self._get_parents(folder)
            path = (gp_name if gp_name else p_name,  # type: ignore
                    p_name if gp_name else None, folder.name)
        try:  # SUBCATEGORY
            parent = self._id_to_folder[folder.parent_id]
            path = (parent.name, folder.name, None)
        except KeyError:  # CATEGORY
            path = (folder.name, None, None)

        return path

    def _get_parents(self, folder: Folder) -> tuple[str, str | None]:
        """Get parent name and grand parent name, if exists."""

        p_folder = self._id_to_folder[folder.parent_id]  # type: ignore
        gp_folder = self._id_to_folder.get(p_folder.parent_id)  # type: ignore
        return p_folder.name, gp_folder.name if gp_folder else None  # type: ignore
