import itertools
from collections import deque
from typing import Iterable

from catalog.models import Folder

import crud

from sqlalchemy.orm import Session

from . import utils as u
from .tavria_typing import Path


class PathesToCreate:

    __categories: deque[Path] = deque()
    __subcategories: deque[Path] = deque()
    __groups: deque[Path] = deque()

    def add(self, path: Path) -> None:
        """Add path in 'to create' list."""

        if path[2]:
            self.__groups.append(path)
        elif not path[1]:
            self.__categories.append(path)
        else:
            self.__subcategories.append(path)

    @property
    def path_batches(self) -> tuple[deque[Path]]:
        return (self.__categories, self.__subcategories, self.__groups)

    def clear(self) -> None:
        self.__categories.clear()
        self.__subcategories.clear()
        self.__groups.clear()


class Catalog:

    _url: str
    _db_session: Session

    _db_folders: list[Folder]
    _ids_with_childs: set[int] = set()
    _deprecated_ids: set[int] = set()
    _ids_to_actualize: deque[int] = deque()
    _ids_to_deprecate: set[int] = set()
    #  hash tables:
    _id_to_folder: dict[int, Folder] = {}
    _path_to_id: dict[Path, int] = {}

    _to_create = PathesToCreate()

    async def initialize(self, url: str, db_session: Session) -> None:
        self._url = url
        self._db_session = db_session

        self._db_folders = await crud.get_folders(db_session)

        self._get_ids_with_childs()

        for folder in self._db_folders:
            self._sort_deprecated(folder)
            self._update_tables(folder)

    def _get_ids_with_childs(self) -> None:
        for folder in self._db_folders:
            if (folder.parent_id and folder.parent_id
                not in self._ids_with_childs):
                self._ids_with_childs.add(folder.parent_id)

    def _sort_deprecated(self, folder: Folder) -> None:
        (self._deprecated_ids.add(folder.id) if folder.deprecated  # type: ignore
            else self._ids_to_deprecate.add(folder.id))  # type: ignore

    def _update_tables(self, folder: Folder) -> None:
            self._id_to_folder[folder.id] = folder
            self._path_to_id[self._get_path(folder)] = folder.id

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

    async def update(self) -> None:
        for path in u.get_page_catalog_pathes(self._url):
            if path in self._path_to_id:
                self._actualize_path(path)
            else:
                self._to_create.add(path)

        await self._create_new_folders()

        if any((self._ids_to_deprecate, self._ids_to_actualize)):
            await crud.switch_deprecated(self._to_switch, self._db_session)

    def _actualize_path(self, path: Path) -> None:
        id_ = self._path_to_id[path]
        if id_ in self._ids_to_deprecate:
            self._ids_to_deprecate.remove(id_)
        if id_ in self._deprecated_ids:
            self._deprecated_ids.remove(id_)
            self._ids_to_actualize.append(id_)

    async def _create_new_folders(self) -> None:
        for batch in self._to_create.path_batches:
            new_folders = [Folder(name=u.get_folder_name(path),
                                  parent_id=self._get_parent_id(path))
                           for path in batch]
            await crud.add_instances(new_folders, self._db_session)
            self._id_to_folder.update({_.id: _ for _ in new_folders})
            self._path_to_id.update(zip(self._to_create.path_batches,
                                        (_.id for _ in new_folders)))

        self._to_create.clear()

    def _get_parent_id(self, path: Path) -> int | None:
        if not any((path[1], path[2])):
            return None
        try:
            return self._path_to_id[u.cut_path(path)]
        except KeyError:
            return self._get_parent_id(u.cut_path(path))

    @property
    def _to_switch(self) -> Iterable[Folder]:
        return (self._id_to_folder[id_] for id_ in
                itertools.chain(self._ids_to_deprecate,
                                self._ids_to_actualize))

    def get_id_by_path(self, path: Path) -> int:
        """Return id of folder, described by path."""
        return self._path_to_id[path]


catalog = Catalog()



    

    # def _get_db_folders_data(self) -> None:
    #     """NOTE: Should not be used with new objects!"""

    #     for folder in self._folders_in_db:
    #         if folder.parent_id and folder.parent_id not in self._has_childs:
    #             self._has_childs.add(folder.parent_id)  # type: ignore
    #         self._id_to_folder[folder.id] = folder  # type: ignore

    # def _get_path_to_id(self) -> None:
    #     """NOTE: Should not be used with new objects!"""

    #     for folder in self._folders_in_db:
    #         if not folder.parent_id:  # CATEGORY
    #             path = (folder.name, None, None)
    #         elif folder.id in self._has_childs:  # SUBCATEGORY
    #             c_name = self._id_to_folder[folder.parent_id].name  # type: ignore
    #             path = (c_name, folder.name, None)  # type: ignore
    #         else:  # GROUP
    #             p_name, gp_name = self._get_group_parents(folder)
    #             path = (gp_name if gp_name else p_name,  # type: ignore
    #                     p_name if gp_name else None,
    #                     folder.name)
    #         self._path_to_id[path] = folder.id  # type: ignore

    # def _get_group_parents(self, folder: Folder) -> tuple[str, str | None]:
    #     """Get parent name and grand parent name, if exists."""

    #     p_folder = self._id_to_folder[folder.parent_id]  # type: ignore
    #     gp_folder = self._id_to_folder.get(p_folder.parent_id)  # type: ignore
    #     return p_folder.name, gp_folder.name if gp_folder else None  # type: ignore

    # def _process_page_data(self) -> None:
    #     for path in u.get_page_catalog_pathes(self._url):
    #         try:  # folder already exists
    #             self._check_id_for_deprecation(self._path_to_id[path])
    #         except KeyError:  # folder is new
    #             self._to_create.add(path)

    # async def _create_new_folders(self) -> None:
    #     new_folders = [Folder(name=u.get_folder_name(path),
    #                           parent_id=self._get_parent_id(path))
    #                    for path in self._to_create.path_batches]
    #     await crud.add_instances(new_folders, self._db_session)
    #     self._id_to_folder.update({_.id: _ for _ in new_folders})
    #     self._path_to_id.update(zip(self._to_create.path_batches,
    #                                 (_.id for _ in new_folders)))
    #     self._to_create.clear()

        # for pathes in self._pathes_to_create.items:
        #     folders_to_save = []
        #     path_to_folder = {}
        #     for path in pathes:
        #         new_folder = Folder(name=u.get_folder_name(path),
        #                             parent_id=self._get_parent_id(path))
        #         folders_to_save.append(new_folder)
        #         path_to_folder[path] = new_folder

        #     await crud.add_instances(folders_to_save, self._db_session)
        #     self._id_to_folder.update({_.id: _ for _ in folders_to_save})
        #     self._path_to_id.update({path: folder.id for path, folder  # type: ignore
        #                             in path_to_folder.items()})
