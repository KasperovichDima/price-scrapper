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

        assert path[0]
        if path[2]:
            self.__groups.append(path)
        elif not path[1]:
            self.__categories.append(path)
        else:
            self.__subcategories.append(path)

    @property
    def path_batches(self) -> Iterable[deque[Path]]:
        return (batch for batch in
                (self.__categories, self.__subcategories, self.__groups)
                if batch)


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

    def get_id_by_path(self, path: Path) -> int:
        """Return id of folder, described by path."""
        assert self._path_to_id
        return self._path_to_id[path]

    async def initialize(self, url: str, db_session: Session) -> None:
        self._url = url
        self._db_session = db_session

        self._db_folders = await crud.get_folders(db_session)
        self._collect_db_folders_data()
        self._path_to_id = {self._get_path(folder): folder.id
                            for folder in self._db_folders}

    def _collect_db_folders_data(self) -> None:
        """Get ids_with_childs, deprecated
        ids and id_to_folder in one path."""
        for folder in self._db_folders:
            self._check_for_childs(folder)
            self._sort_deprecated(folder)
            self._id_to_folder[folder.id] = folder

    def _check_for_childs(self, folder: Folder) -> None:
        if (folder.parent_id and folder.parent_id
                not in self._ids_with_childs):
            self._ids_with_childs.add(folder.parent_id)

    def _sort_deprecated(self, folder: Folder) -> None:
        (self._deprecated_ids.add(folder.id) if folder.deprecated  # type: ignore  # noqa: E501
         else self._ids_to_deprecate.add(folder.id))  # type: ignore

    def _get_path(self, folder: Folder) -> Path:
        if self._folder_is_group(folder):
            p_name, gp_name = self._get_parents(folder)
            path = (gp_name if gp_name else p_name,  # type: ignore
                    p_name if gp_name else None, folder.name)
        else:
            try:  # SUBCATEGORY
                parent = self._id_to_folder[folder.parent_id]
                path = (parent.name, folder.name, None)
            except KeyError:  # CATEGORY
                path = (folder.name, None, None)

        return path

    def _folder_is_group(self, folder: Folder) -> bool:
        return folder.parent_id and folder.id not in self._ids_with_childs

    def _get_parents(self, folder: Folder) -> tuple[str, str | None]:
        """Get parent name and grand parent name, if exists."""

        p_folder = self._id_to_folder[folder.parent_id]  # type: ignore
        gp_folder = self._id_to_folder.get(p_folder.parent_id)  # type: ignore
        return (p_folder.name, gp_folder.name
                if gp_folder else None)

    async def update(self) -> None:
        for path in u.get_page_catalog_pathes(self._url):
            if path in self._path_to_id:
                self._actualize_path(path)
            else:
                self._to_create.add(path)

        await self._create_new_folders()

        if any((self._ids_to_deprecate, self._ids_to_actualize)):
            await crud.switch_deprecated(self._to_switch, self._db_session)

        self._clear()

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
            self._path_to_id.update(zip(batch, (_.id for _ in new_folders)))

    def _get_parent_id(self, path: Path) -> int | None:
        if not any((path[1], path[2])):
            return None
        if parent_id := self._path_to_id.get(u.cut_path(path)):
            return parent_id
        return self._get_parent_id(u.cut_path(path))

    @property
    def _to_switch(self) -> Iterable[Folder]:
        return (self._id_to_folder[id_] for id_ in
                itertools.chain(self._ids_to_deprecate,
                                self._ids_to_actualize))

    # def _cleaer(self) -> None:
    #     del Catalog._url
    #     del Catalog._db_session
    #     self._db_folders.clear()
    #     self._ids_with_childs.clear()
    #     self._deprecated_ids.clear()
    #     self._ids_to_actualize.clear()
    #     self._ids_to_deprecate.clear()
    #     self._id_to_folder.clear()
    #     del Catalog._to_create


catalog = Catalog()
