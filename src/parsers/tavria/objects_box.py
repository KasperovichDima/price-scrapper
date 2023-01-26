"""
ObjectsBox class for handling new and existing objects.
NOTE:
This class must be fast, do perfomance
is before readability in some places.
"""
import itertools
from typing import Iterable

from catalog.models import BaseCatalogElement, Product
from catalog.utils import get_class_by_type

import crud

from sqlalchemy import Column
from sqlalchemy.orm import Session


class ObjectsBox:
    """Takes care of new objects, their validating,
    saving, actualization and deactualization."""

    __slots__ = ('_cur_type', '_now_deprecated', '_in_db_objects',
                 '_objects_to_save', '_db_session')

    def __init__(self, db_session: Session) -> None:
        self._db_session = db_session
        self._cur_type: Column | None = None

        self._now_deprecated: set[BaseCatalogElement] = set()
        self._in_db_objects: set[BaseCatalogElement] = set()

        self._objects_to_save: list[BaseCatalogElement] = []

    async def add(self, objects: Iterable[BaseCatalogElement]) -> None:
        """Add objects in box. Do not care about the
        rest. Box know what to do with your objects.
        NOTE: It must be objects of one factory, i.e.
              they must have same type and parent id."""
        # TODO: We can switch _new_objects to
        #       set to avoid duplicated names problem.

        box_is_ready = False
        for obj_ in objects:
            if not box_is_ready:
                await self._reconfigure_box(obj_)
                box_is_ready = True
            self._in_db_objects.remove(obj_) if obj_ in self._in_db_objects\
                else self._objects_to_save.append(obj_)

    async def _reconfigure_box(self, obj_: BaseCatalogElement) -> None:
        """Check new objects type and refresh self fields, if required."""
        async def refresh_db_objects():
            cls_ = get_class_by_type(obj_.el_type)
            type_ = None if cls_ is Product else [obj_.el_type]  # FIXME
            objects = await crud.get_elements(cls_, self._db_session,
                                              el_type=type_)
            self._in_db_objects.update(objects)

        def refresh_deprecated():
            self._now_deprecated = {_ for _ in self._in_db_objects
                                    if _.deprecated}

        if not self._cur_type or self._cur_type is not obj_.el_type:
            await refresh_db_objects()
            refresh_deprecated()
            self._cur_type = obj_.el_type

    async def save_all(self) -> None:
        """Save new objects to databaseand actualize their status.
        TODO: Objects must be saved on every parent id change."""
        await crud.add_instances(self._objects_to_save, self._db_session)
        self._actualize()
        self._clear_all()

    def _actualize(self) -> None:
        to_deprecate = [_ for _ in self._in_db_objects if not _.deprecated]
        to_actualize = self._now_deprecated - self._in_db_objects
        if to_deprecate or to_actualize:
            for _ in list(itertools.chain(to_deprecate, to_actualize)):
                _.deprecated = not _.deprecated
            self._db_session.commit()

    def _clear_all(self) -> None:
        self._now_deprecated.clear()
        self._in_db_objects.clear()
        self._objects_to_save.clear()
