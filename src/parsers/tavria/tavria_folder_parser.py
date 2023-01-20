from catalog.models import Folder

from project_typing import ElType

from .tavria_base_catalog_parser import TavriaBaseCatalogParser


class TavriaFolderParser(TavriaBaseCatalogParser):

    _create_class = Folder

    async def _process_factory_objects(self) -> None:
        """Factory objects processing is
        inside the _get_factory_objects loop."""
        self._factory_objects.clear()

    async def _get_factory_objects(self):
        for type_ in (_ for _ in ElType if _ is not ElType.PRODUCT):
            await self.__process_factories_type(type_)

    async def __process_factories_type(self, type_: ElType) -> None:
        self.__get_type_objects(type_)
        self._mark_depricated(type_)
        self._unmark_depricated()
        await self._save_objects()
        self._db_objects.extend(self._factory_objects)
        self._refresh_factory_table()

    def __get_type_objects(self, type_: ElType) -> None:
        for factory in self.factories[type_]:
            self._factory_objects.update(factory.get_objects())
