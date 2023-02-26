"""
Catalog conftest.
TODO: Remove it and use catalog from parser test.
"""
from catalog.models import Folder

import crud

from database import TestSession

import pytest_asyncio


@pytest_asyncio.fixture
async def fake_db_del_content():
    """Fake content for delete folder test."""
    folders = {
            1: Folder(name='Alcohol'),
            2: Folder(name='Hard', parent_id=1),
            3: Folder(name='Easy', parent_id=1),
            4: Folder(name='NonAlcohol', parent_id=1),
            5: Folder(name='Vine', parent_id=2),
            6: Folder(name='Vodka', parent_id=2),
            7: Folder(name='Beer', parent_id=3),
            8: Folder(name='Cocktails', parent_id=3),
            9: Folder(name='Juices', parent_id=4),
            10: Folder(name='Water', parent_id=4),
    }

    async with TestSession() as test_session:
        await crud.add_instances(folders.values(), test_session)
        yield folders.values()
        folders.pop(3)
        folders.pop(7)
        folders.pop(8)
        to_delete = list(folders.values())
        await crud.delete_cls_instances(to_delete, test_session)
