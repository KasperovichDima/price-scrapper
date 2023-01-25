import itertools
from typing import Iterable

from catalog.models import BaseCatalogElement, Product
from catalog.utils import get_class_by_type

import crud

from sqlalchemy import Column
from sqlalchemy.orm import Session


class ObjectsBox:

    cur_type: Column | None = None

    now_deprecated: set[BaseCatalogElement] = set()
    in_db_objects: set[BaseCatalogElement] = set()

    new_objects: list[BaseCatalogElement] = []

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    async def add(self, objects: Iterable[BaseCatalogElement]) -> None:
        refreshed = False
        for obj_ in objects:
            if not refreshed:
                await self.refresh_data(obj_)
                refreshed = True
            self.in_db_objects.remove(obj_) if obj_ in self.in_db_objects\
                else self.new_objects.append(obj_)

    async def refresh_data(self, obj_: BaseCatalogElement) -> None:

        async def refresh_db_objects():
            cls_ = get_class_by_type(obj_.el_type)
            type_ = None if cls_ is Product else [obj_.el_type]  # TODO: Fix!
            objects = await crud.get_elements(cls_, self.db_session,
                                              el_type=type_)
            self.in_db_objects.update(objects)

        def refresh_deprecated():
            self.now_deprecated = set(_ for _ in self.in_db_objects
                                      if _.deprecated)

        if not self.cur_type or self.cur_type != obj_.el_type:
            await refresh_db_objects()
            refresh_deprecated()
            self.cur_type = obj_.el_type

    async def save_all(self) -> None:
        """TODO: Objects must be saved on every parent id change."""
        await crud.add_instances(self.new_objects, self.db_session)
        self.change_deprecated_status()
        self.clear_all()

    def change_deprecated_status(self) -> None:
        to_deprecate = [_ for _ in self.in_db_objects if not _.deprecated]
        to_actualize = self.now_deprecated - self.in_db_objects
        if to_deprecate or to_actualize:
            for _ in list(itertools.chain(to_deprecate, to_actualize)):
                _.deprecated = not _.deprecated
            self.db_session.commit()

    def clear_all(self) -> None:
        self.now_deprecated.clear()
        self.in_db_objects.clear()
        self.new_objects.clear()
