"""Catalog conftest."""
import asyncio

from catalog.models import Folder

import crud

from project_typing import ElType

import pytest


@pytest.fixture
def fake_db_del_content(fake_session):
    """Fake content for delete folder test."""
    folders = {
            1: Folder(name='Alcohol', el_type=ElType.CATEGORY),
            2: Folder(name='Hard', el_type=ElType.SUBCATEGORY, parent_id=1),
            3: Folder(name='Easy', el_type=ElType.SUBCATEGORY, parent_id=1),
            4: Folder(name='NonAlcohol', el_type=ElType.SUBCATEGORY, parent_id=1),  # noqa: E501
            5: Folder(name='Vine', el_type=ElType.GROUP, parent_id=2),
            6: Folder(name='Vodka', el_type=ElType.GROUP, parent_id=2),
            7: Folder(name='Beer', el_type=ElType.GROUP, parent_id=3),
            8: Folder(name='Cocktails', el_type=ElType.GROUP, parent_id=3),
            9: Folder(name='Juices', el_type=ElType.GROUP, parent_id=4),
            10: Folder(name='Water', el_type=ElType.GROUP, parent_id=4),
    }

    asyncio.run(crud.add_instances(folders.values(), fake_session))
    yield folders.values()
    folders.pop(3)
    folders.pop(7)
    folders.pop(8)
    to_delete = list(folders.values())
    asyncio.run(crud.delete_cls_instances(to_delete, fake_session))
