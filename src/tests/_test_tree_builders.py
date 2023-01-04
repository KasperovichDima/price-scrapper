"""TreeBuilders unit tests."""
from typing import Iterable
import asyncio
import aiohttp

from catalog.models import Folder

from core.parsers import TreeBuilder as TavriaTreeBuilder
from core.parsers.tavria import ProductFactory

import crud

from database import TestSession

from .constants import TAVRIA_TEST_URL
from .constants import FAKE_GROUP_URL
from .references.references import tavria_tree_builder_result


async def just_pass(_): ...


def fake_parent_id():
    return 1


class TestTavriaTreeBuilders:
    """Tree builders test class."""

    def test_tavria_folders_creation(self):
        """Test of Tavria TreeBuilder folders creation."""
        with TestSession() as session:
            #  mock product creation
            TavriaTreeBuilder.__create_products = just_pass
            TavriaTreeBuilder()(TAVRIA_TEST_URL, session)
            all_folders: Iterable[Folder] = crud.get_folders(session)
        result = [(_.name, _.parent_id, _.el_type.value) for _ in all_folders]

        assert result == tavria_tree_builder_result


    def test_tavria_products_factory(self):
        """Test of Tavria TreeBuilder products creation."""
        asyncio.run(self.__test_tavria_products_factory())

    async def __test_tavria_products_factory(self):
        ProductFactory._parent_id = fake_parent_id
        factory = ProductFactory(url=FAKE_GROUP_URL,
                                 category_name='Bakaleya',
                                 subcategory_name='Krupy',
                                 group_name='Rys')
        async with aiohttp.ClientSession() as session:
            result = await factory.get_objects(session)
        print(result)

        
