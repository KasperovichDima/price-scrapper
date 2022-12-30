"""TreeBuilders unit tests."""
from typing import Iterable

from catalog.models import Folder

from core.parsers import TreeBuilder as TavriaTreeBuilder

import crud

from database import TestSession

from .constants import TAVRIA_TEST_URL
from .references.references import tavria_tree_builder_result


async def just_pass(_):...


class TestTreeBuilders:
    """Tree builders test class."""

    def test_tavria(self):
        """Test of Tavria TreeBuilder"""
        with TestSession() as session:
            TavriaTreeBuilder._create_products = just_pass
            TavriaTreeBuilder()(TAVRIA_TEST_URL, session)
            all_folders: Iterable[Folder] = crud.get_folders(session)
        result = [(_.name, _.parent_id, _.el_type.value) for _ in all_folders]

        assert result == tavria_tree_builder_result
