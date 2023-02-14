import itertools
from collections import defaultdict, deque, namedtuple
from typing import Iterable

from catalog.models import Folder

import crud

from project_typing import ElType

from sqlalchemy.orm import Session

from . import utils as u
from .tavria_typing import Path


IdParentID = namedtuple('IdParentID', ('id parent_id'))
PathToIdParentID = dict[Path, IdParentID]


class Catalog:

    _folders_in_db: list[Folder]  # TODO: Make property

    _has_childs: set[int] = set()
    _deprecated_ids: set[int] = set()
    _ids_to_actualize: deque[int] = deque()
    _ids_to_deprecate: set[int] = set()
    _id_to_folder: dict[int, Folder] = {}
    _path_to_id_parent_id: PathToIdParentID = {}
    _pathes_to_create: defaultdict[ElType, deque[Path]] = defaultdict(deque)

    def __init__(self, url: str, db_session: Session) -> None:
        self._url = url
        self._db_session = db_session

    async def update(self) -> None:
        self._folders_in_db = await crud.get_folders(self._db_session)
        self._get_db_folders_data()
        self._get_path_to_id_parent_id(self._folders_in_db)
        del self._folders_in_db
        self._process_page_data()
        await self._create_new_folders()
        await self._switch_deprecated()

    def _get_db_folders_data(self) -> None:
        for folder in self._folders_in_db:
            if folder.parent_id and folder.parent_id not in self._has_childs:
                self._has_childs.add(folder.parent_id)  # type: ignore
            (self._deprecated_ids.add(folder.id) if folder.deprecated  # type: ignore
                else self._ids_to_deprecate.add(folder.id))  # type: ignore
            self._id_to_folder[folder.id] = folder  # type: ignore

    def _get_path_to_id_parent_id(self, folders: Iterable[Folder]) -> None:
        """NOTE: Should not be used for new objects!"""

        for folder in folders:
            if not folder.parent_id:  # CATEGORY
                path = (folder.name, None, None)
            elif folder.id in self._has_childs:  # SUBCATEGORY
                c_name = self._id_to_folder[folder.parent_id].name  # type: ignore
                path = (c_name, folder.name, None)  # type: ignore
            else:  # GROUP
                p_name, gp_name = self._get_group_parents(folder)
                path = (gp_name if gp_name else p_name,  # type: ignore
                        p_name if gp_name else None,
                        folder.name)
            self._path_to_id_parent_id[path] = IdParentID(folder.id,  # type: ignore
                                                          folder.parent_id)

    def _get_group_parents(self, folder: Folder) -> tuple[str, str | None]:
        """Get parent name and grand parent name, if exists."""

        p_folder = self._id_to_folder[folder.parent_id]  # type: ignore
        gp_folder = self._id_to_folder.get(p_folder.parent_id)  # type: ignore
        return p_folder.name, gp_folder.name if gp_folder else None  # type: ignore

    def _process_page_data(self) -> None:
        for path in u.get_page_catalog_folders(self._url):
            try:  # folder already exists
                path_id: int = self._path_to_id_parent_id[path].id
                self._check_id_for_deprecation(path_id)
            except KeyError:  # new folder
                self._add_path_to_create(path)

    def _check_id_for_deprecation(self, id_: int) -> None:
        if id_ in self._ids_to_deprecate:
            self._ids_to_deprecate.remove(id_)
        if id_ in self._deprecated_ids:
            self._deprecated_ids.remove(id_)
            self._ids_to_actualize.append(id_)

    def _add_path_to_create(self, path: Path) -> None:
        if path[2]:
            self._pathes_to_create[ElType.GROUP].append(path)
        elif not path[1]:
            self._pathes_to_create[ElType.CATEGORY].append(path)
        else:
            self._pathes_to_create[ElType.SUBCATEGORY].append(path)

    async def _create_new_folders(self) -> None:
        for type_, pathes in self._pathes_to_create.items():
            if not pathes:
                continue
            folders_to_save = []
            for path in pathes:
                folders_to_save.append(
                    Folder(name=self._get_folder_name(path),
                           parent_id=self._get_parent_id(path),
                           el_type=type_)
                )

                folders_to_save[-1].has_childs = True if not path[2] else False

            await crud.add_instances(folders_to_save, self._db_session)

            for folder in folders_to_save:
                if folder.has_childs:
                    self._has_childs.add(folder.id)

            self._id_to_folder.update({_.id: _ for _ in folders_to_save})
            self._get_path_to_id_parent_id(folders_to_save)

    @staticmethod
    def _get_folder_name(path: Path) -> str:
        for name in path[::-1]:
            if name:
                return name
        raise ValueError('All names are empty.')

    def _get_parent_id(self, path: Path) -> int | None:
        if not path[0]:
            return None
        for ind in range(len(path) - 1, -1, -1):
            if path[ind]:
                path = path[:ind] + (None,) + path[ind + 1:]
                try:
                    return self._path_to_id_parent_id[path].id
                except KeyError:
                    return self._get_parent_id(path)

    async def _switch_deprecated(self) -> None:
        if not any((self._ids_to_deprecate, self._ids_to_actualize)):
            return
        to_switch = (
            self._id_to_folder[id_] for id_ in
            itertools.chain(self._ids_to_deprecate,
                            self._ids_to_actualize)
        )
        await crud.switch_deprecated(to_switch, self._db_session)
