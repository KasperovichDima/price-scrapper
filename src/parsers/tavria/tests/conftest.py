"""Parser conftest."""
import asyncio

from catalog.models import BaseCatalogElement, Folder, Product

import crud

from project_typing import ElType
from project_typing import folder_types

import pytest


@pytest.fixture
def fake_parser_db(fake_session):
    """Fill database catalog with fake content required for parser tests."""

    content: list[BaseCatalogElement] = [
        #  Actual fodlers:
        Folder(name='Бакалія', el_type=ElType.CATEGORY),
        Folder(name='Крупи', el_type=ElType.SUBCATEGORY, parent_id=1),
        Folder(name='Гречана крупа', el_type=ElType.GROUP, parent_id=2),
        Folder(name='Кукурудзяна крупа', el_type=ElType.GROUP, parent_id=2),
        Folder(name='Рис', el_type=ElType.GROUP, parent_id=2),
        Folder(name='Протеїнові батончики', el_type=ElType.GROUP, parent_id=1),
        Folder(name='Їжа швидкого приготування', el_type=ElType.GROUP, parent_id=1),  # noqa: E501
        #  Deprecated folders:
        Folder(name='Deprecated folder 1', el_type=ElType.CATEGORY),
        Folder(name='Deprecated folder 2', el_type=ElType.SUBCATEGORY, parent_id=8),  # noqa: E501
        Folder(name='Deprecated folder 3', el_type=ElType.GROUP, parent_id=9),
        #  Actual products:
        Product(name="Крупа Українська Зірка Гречана 1 кг", parent_id=3, prime_cost=49.93),  # noqa: E501
        Product(name="Крупа Хуторок Гречана 800 г", parent_id=3, prime_cost=59.98),  # noqa: E501
        Product(name="Крупа Сквирянка Гречана 800 г", parent_id=3, prime_cost=62.15),  # noqa: E501
        Product(name="Крупа Сквирянка Гречана 800 г непропарена", parent_id=3, prime_cost=65.75),  # noqa: E501
        Product(name="Крупа Українська Зірка 800 г Кукурудзяна", parent_id=4, prime_cost=12.42),  # noqa: E501
        Product(name="Крупа Терра Кукурудзяна 5х80 г", parent_id=4, prime_cost=27.68, deprecated=True),  # noqa: E501
        Product(name="Крупа Моя Країна Кукурудзяна 600 г", parent_id=4, prime_cost=28.63),  # noqa: E501
        Product(name="Крупа Жменька Кукурудзяна 300 г картон", parent_id=4, prime_cost=17.21),  # noqa: E501
        Product(name="Рис круглий ваг.", parent_id=5, prime_cost=34.85),
        Product(name="Рис Хуторок 800 г круглий", parent_id=5, prime_cost=57.14),  # noqa: E501
        Product(name="Рис Трапеза 500 г Басматі пропарений", parent_id=5, prime_cost=77.11),  # noqa: E501
        Product(name="Рис Хуторок 800 г пропарений", parent_id=5, prime_cost=60.32),  # noqa: E501
        Product(name="Батончик протеїновий Healthy Meal 40 г з фісташками глазур.", parent_id=6, prime_cost=37.89),  # noqa: E501
        Product(name="Батончик протеїновий Vale 4Energy 40 г вишня", parent_id=6, prime_cost=12.47),  # noqa: E501
        Product(name="Батончик протеїновий Vale 40 г полуниця", parent_id=6, prime_cost=12.47),  # noqa: E501
        Product(name="Батончик Biotech Protein Bar 70 г Strawberry", parent_id=6, prime_cost=74.58),  # noqa: E501
        Product(name="Локшина Роллтон яєчна 75 г стак. зі смаком Курки по-домашньому", parent_id=7, prime_cost=22.10),  # noqa: E501
        Product(name="Пюре картопл. Эко 30 г Вершкове", parent_id=7, prime_cost=8.41),  # noqa: E501
        Product(name="Каша Терра вівсяна з верш. 38 г з абрикосом", parent_id=7, prime_cost=5.65),  # noqa: E501
        Product(name="Каша Терра 38 г вівсяна з яблуком та корицею", parent_id=7, prime_cost=5.65),  # noqa: E501
        #  Deprecated products:
        Product(name="Deprecated product 1", parent_id=3, prime_cost=100),
        Product(name="Deprecated product 2", parent_id=3, prime_cost=110),
        Product(name="Deprecated product 3", parent_id=5, prime_cost=120),
        Product(name="Deprecated product 4", parent_id=5, prime_cost=130),
    ]
    asyncio.run(crud.add_instances(content, fake_session))
    yield content
    folders = [_ for _ in content if _.el_type in folder_types]
    asyncio.run(crud.delete_cls_instances(folders, fake_session))
