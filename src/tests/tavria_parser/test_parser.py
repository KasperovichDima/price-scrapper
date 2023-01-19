"""Parser tests."""
import crud

from parsers.tavria import TavriaFolderParser
from parsers.tavria import TavriaProductParser

import pytest

from . import classes as c
from . import reference as r


class TestTavriaParser:
    """Test class for tavria parser."""

    fake_home_url = 'file:///home/kasper/Documents/projects/monitoring'\
                    '/src/tests/tavria_parser/html/tavria_home.html'

    @pytest.mark.asyncio
    async def test_parser_all_cases(self, fake_session, fake_parser_db):
        factories = c.FactoryCreator_test(self.fake_home_url)()
        await TavriaFolderParser(factories, fake_session)()
        await TavriaProductParser(factories, fake_session)()
        result_folders = await crud.get_folders(fake_session)
        result_products = await crud.get_products(fake_session)
        result_actual_folder_names = set(_.name for _ in result_folders
                                         if not _.deprecated)
        result_deprecated_folder_names = set(_.name for _ in result_folders
                                             if _.deprecated)
        result_actual_product_names = set(_.name for _ in result_products
                                          if not _.deprecated)
        result_deprecated_product_names = set(_ .name for _ in result_products
                                              if _.deprecated)

        assert result_actual_folder_names == r.ref_actual_folder_names
        assert result_deprecated_folder_names == r.ref_deprecated_folder_names
        assert result_actual_product_names == r.ref_actual_product_names
        assert result_deprecated_product_names\
            == r.ref_deprecated_product_names
