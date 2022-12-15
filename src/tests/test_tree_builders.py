"""TreeBuilders unit tests."""
from typing import Iterable

from catalog.models import Folder

from core.parsers import TreeBuilder as TavriaTreeBuilder

from database import TestSession

from .constants import TAVRIA_TEST_URL
from .references.references import tavria_tree_builder_result


class TestTreeBuilders:
    """Tree builders test class."""

    def test_tavria(self):
        """Test of Tavria TreeBuilder"""
        with TestSession() as session:
            TavriaTreeBuilder(TAVRIA_TEST_URL, session)
            folders: Iterable[Folder] = session.query(Folder).all()
        result = [(_.name, _.parent_id, _.type.value) for _ in folders]

        assert result == tavria_tree_builder_result
