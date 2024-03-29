from collections import deque
from typing import Iterable

from catalog.models import Folder

import crud

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from . import utils as u
from .support_classes import FolderPath, ToSwitchStatus


class PathesToCreate:
    """Implementation of 'to create' list. Can
    save and return folder pathes in correct order."""

    __categories: deque[FolderPath] = deque()
    __subcategories: deque[FolderPath] = deque()
    __groups: deque[FolderPath] = deque()

    def add(self, path: FolderPath) -> None:
        """Add path in 'to create' list."""

        assert path[0]
        if path[2]:
            self.__groups.append(path)
        elif not path[1]:
            self.__categories.append(path)
        else:
            self.__subcategories.append(path)

    @property
    def path_batches(self) -> Iterable[deque[FolderPath]]:
        return (batch for batch in (self.__categories,
                                    self.__subcategories,
                                    self.__groups)
                                if batch)  # noqa: E127


class Catalog:
    """
    Implementation of Catalog protocol.
    NOTE: 'initialize' method must be awaited before using the catalog.
    """

    _url: str
    _session_maker: async_sessionmaker[AsyncSession]

    _db_folders: list[Folder]
    _ids_with_childs: set[int]
    _deprecated_ids: set[int]
    _ids_to_actualize: deque[int]
    _ids_to_deprecate: set[int]

    _id_to_folder: dict[int, Folder]
    _path_to_id: dict[FolderPath, int]

    _to_create: PathesToCreate

    async def initialize(
            self, url: str,
            session_maker: async_sessionmaker[AsyncSession]
            ) -> None:
        """Async method, that must be called before using the object.
        Provides the object with the resources, required for it's work"""

        self._url = url
        self._session_maker = session_maker

        self._ids_with_childs: set[int] = set()
        self._deprecated_ids: set[int] = set()
        self._ids_to_deprecate: set[int] = set()
        self._ids_to_actualize: deque[int] = deque()

        self._id_to_folder: dict[int, Folder] = {}
        self._path_to_id: dict[FolderPath, int] = {}

        async with self._session_maker() as db_session:
            self._db_folders = await crud.get_folders(db_session)
        self._collect_db_folders_data()
        self._path_to_id = {self._get_path(folder): folder.id
                            for folder in self._db_folders}

        self._post_init_clear()

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
        (self._deprecated_ids.add(folder.id) if folder.deprecated
         else self._ids_to_deprecate.add(folder.id))

    def _get_path(self, folder: Folder) -> FolderPath:
        if self._folder_is_group(folder):
            p_name, gp_name = self._get_parents(folder)
            path: FolderPath = (gp_name if gp_name else p_name,
                          p_name if gp_name else None, folder.name)
        else:
            try:  # SUBCATEGORY
                parent = self._id_to_folder[folder.parent_id]
                path = (parent.name, folder.name, None)
            except KeyError:  # CATEGORY
                path = (folder.name, None, None)

        return path

    def _folder_is_group(self, folder: Folder) -> bool:
        return (folder.parent_id is not None
                and (folder.id not in self._ids_with_childs))

    def _get_parents(self, folder: Folder) -> tuple[str, str | None]:
        """Get parent name and grand parent name, if exists."""

        p_folder = self._id_to_folder[folder.parent_id]
        gp_folder = self._id_to_folder.get(p_folder.parent_id)
        return (p_folder.name, gp_folder.name
                if gp_folder else None)

    def _post_init_clear(self) -> None:
        del self._ids_with_childs
        del self._db_folders

    def get_id_by_path(self, path: FolderPath) -> int:
        assert self._path_to_id
        return self._path_to_id[path]

    async def update(self) -> None:
        self._to_create = PathesToCreate()

        for path in u.get_page_catalog_pathes(self._url):
            if path in self._path_to_id:
                self._update_path_status(path)
            else:
                self._to_create.add(path)

        await self._create_new_folders()

        if any((self._ids_to_deprecate, self._ids_to_actualize)):
            to_switch = ToSwitchStatus(
                cls_=Folder,
                ids_to_depr=self._ids_to_deprecate,
                ids_to_undepr=self._ids_to_actualize
            )
            async with self._session_maker() as db_session:
                async with db_session.begin():
                    await crud.switch_deprecated(to_switch, db_session)
                    await db_session.commit()

        self._post_update_clear()

    def _update_path_status(self, path: FolderPath) -> None:
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
            async with self._session_maker() as db_session:
                await crud.add_instances(new_folders, db_session)
                await db_session.commit()
            self._id_to_folder.update({_.id: _ for _ in new_folders})
            self._path_to_id.update(zip(batch, (_.id for _ in new_folders)))

    def _get_parent_id(self, path: FolderPath) -> int | None:
        if not any((path[1], path[2])):
            return None
        if parent_id := self._path_to_id.get(u.cut_path(path)):
            return parent_id
        return self._get_parent_id(u.cut_path(path))

    def _post_update_clear(self) -> None:
        del self._deprecated_ids
        del self._ids_to_actualize
        del self._ids_to_deprecate
        del self._to_create
        del self._id_to_folder
        del self._url
        del self._session_maker


catalog = Catalog()
