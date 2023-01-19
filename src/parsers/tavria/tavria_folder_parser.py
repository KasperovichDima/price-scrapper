from parsers.tavria.tavria_base_catalog_parser import TavriaBaseCatalogParser

import asyncio
from collections import defaultdict
from collections.abc import Mapping
from functools import singledispatchmethod
from typing import Iterable, MutableSequence

from catalog.models import BaseCatalogElement, Folder, Product
from catalog.utils import get_catalog_class

import crud

from parsers.constants import MAIN_PARSER

from project_typing import ElType

from sqlalchemy.orm import Session

from . import constants as c
from .factory import BaseFactory, ProductFactory
from .factory_creator import FactoryCreator
from .tavria_typing import ObjectParents
from . import utils as u


class TavriaFolderParser(TavriaBaseCatalogParser):

    create_class = Folder

    async def post_create_tasks(self):
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
