"""Parser tests."""
import asyncio
from core.parsers import TavriaParser
import crud
import pytest
from . import reference as r
from . import classes as c


class TestTavriaParser:
    """Test class for tavria parser."""

    # fake_home_url = '/home/kasper/Documents/projects/monitoring/src/tests/tavria_parser/html/tavria_home.html'
    fake_home_url = 'file:///home/kasper/Documents/projects/monitoring/src/tests/tavria_parser/html/tavria_home.html'

    @pytest.mark.asyncio
    async def test_parser_all_cases(self, fake_session, fake_parser_db):
        await asyncio.sleep(0.1)

        factory_creator = c.FactoryCreator_test(self.fake_home_url)

        await TavriaParser(factory_creator).refresh_catalog(fake_session)
        result_folders = await crud.get_folders(fake_session)
        result_products = await crud.get_products(fake_session)
        result_actual_folder_names = set(_.name for _ in result_folders if not _.deprecated)
        result_deprecated_folder_names = set(_.name for _ in result_folders if _.deprecated)
        result_actual_product_names = set(_.name for _ in result_products if not _.deprecated)
        result_deprecated_product_names = set(_ .name for _ in result_products if _.deprecated)

        assert result_actual_folder_names == r.ref_actual_folder_names
        assert result_deprecated_folder_names == r.ref_deprecated_folder_names
        assert result_actual_product_names == r.ref_actual_product_names
        assert result_deprecated_product_names == r.ref_deprecated_product_names
