from catalog.models import Folder

from project_typing import ElType

from .tavria_base_catalog_parser import TavriaBaseCatalogParser


class TavriaFolderParser(TavriaBaseCatalogParser):

    create_class = Folder

    async def process_factory_objects(self):
        self.factory_objects.clear()

    async def get_factory_objects(self):
        for type_ in ElType:
            if type_ is ElType.PRODUCT:
                break
            self.get_objects(type_)
            self.mark_depricated(type_)
            self.unmark_depricated()
            await self.save_objects()
            self.refresh_factory_table()

    def get_objects(self, type_: ElType):
        for factory in self.factories[type_]:
            self.factory_objects.update(factory.get_objects())
