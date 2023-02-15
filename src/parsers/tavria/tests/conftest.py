"""Parser conftest."""
import asyncio
from datetime import date

from catalog.models import BaseCatalogElement, Folder, Product

from core.models import PriceLine

import crud

import pytest

from retailer.models import Retailer
from retailer.retailer_typing import RetailerName

from . import constants as c


@pytest.fixture
def fake_catalog_db(fake_session):
    """Fill database catalog with fake content required for parser tests."""

    catalog: tuple[BaseCatalogElement] = (
        #  Actual fodlers:
        Folder(name='Бакалія'),
        Folder(name='Крупи', parent_id=1),
        Folder(name='Снеки', parent_id=1),
        Folder(name='Гречана крупа', parent_id=2),
        Folder(name='Кукурудзяна крупа', parent_id=2),
        Folder(name='Рис', parent_id=2),
        Folder(name='Протеїнові батончики', parent_id=1),
        Folder(name='Їжа швидкого приготування', parent_id=1),  # noqa: E501
        Folder(name='Чіпси', parent_id=3),  # noqa: E501
        #  Deprecated folders:
        Folder(name='Deprecated folder 1'),
        Folder(name='Deprecated folder 2', parent_id=1),  # noqa: E501
        Folder(name='Deprecated folder 3', parent_id=2),
        #  Actual products:
        Product(name="Крупа Українська Зірка Гречана 1 кг", parent_id=4, prime_cost=49.93),  # noqa: E501
        Product(name="Крупа Хуторок Гречана 800 г", parent_id=4, prime_cost=59.98),  # noqa: E501
        Product(name="Крупа Сквирянка Гречана 800 г", parent_id=4, prime_cost=62.15),  # noqa: E501
        Product(name="Крупа Сквирянка Гречана 800 г непропарена", parent_id=4, prime_cost=65.75),  # noqa: E501
        Product(name="Крупа Українська Зірка 800 г Кукурудзяна", parent_id=5, prime_cost=12.42),  # noqa: E501
        Product(name="Крупа Терра Кукурудзяна 5х80 г", parent_id=5, prime_cost=27.68, deprecated=True),  # noqa: E501
        Product(name="Крупа Моя Країна Кукурудзяна 600 г", parent_id=5, prime_cost=28.63),  # noqa: E501
        Product(name="Крупа Жменька Кукурудзяна 300 г картон", parent_id=5, prime_cost=17.21),  # noqa: E501
        Product(name="Рис круглий ваг.", parent_id=6, prime_cost=34.85),
        Product(name="Рис Хуторок 800 г круглий", parent_id=6, prime_cost=57.14),  # noqa: E501
        Product(name="Рис Трапеза 500 г Басматі пропарений", parent_id=6, prime_cost=77.11),  # noqa: E501
        Product(name="Рис Хуторок 800 г пропарений", parent_id=6, prime_cost=60.32),  # noqa: E501
        Product(name="Батончик протеїновий Healthy Meal 40 г з фісташками глазур.", parent_id=7, prime_cost=37.89),  # noqa: E501
        Product(name="Батончик протеїновий Vale 4Energy 40 г вишня", parent_id=7, prime_cost=12.47),  # noqa: E501
        Product(name="Батончик протеїновий Vale 40 г полуниця", parent_id=7, prime_cost=12.47),  # noqa: E501
        Product(name="Батончик Biotech Protein Bar 70 г Strawberry", parent_id=7, prime_cost=74.58),  # noqa: E501
        Product(name="Локшина Роллтон яєчна 75 г стак. зі смаком Курки по-домашньому", parent_id=8, prime_cost=22.10),  # noqa: E501
        Product(name="Пюре картопл. Эко 30 г Вершкове", parent_id=8, prime_cost=8.41),  # noqa: E501
        Product(name="Каша Терра вівсяна з верш. 38 г з абрикосом", parent_id=8, prime_cost=5.65),  # noqa: E501
        Product(name="Каша Терра 38 г вівсяна з яблуком та корицею", parent_id=8, prime_cost=5.65),  # noqa: E501
        Product(name="Чіпси '7' 70 г зі смаком сметани та зелені (кор.)", parent_id=9, prime_cost=15.00),  # noqa: E501
        Product(name="Чіпси Люкс 71 г бекон", parent_id=9, prime_cost=31.15),
        Product(name="Чіпси Люкс 133 г сир", parent_id=9, prime_cost=45.25),
        #  Deprecated products:
        Product(name="Deprecated product 1", parent_id=4, prime_cost=100),
        Product(name="Deprecated product 2", parent_id=4, prime_cost=110),
        Product(name="Deprecated product 3", parent_id=5, prime_cost=120),
        Product(name="Deprecated product 4", parent_id=5, prime_cost=130),
    )
    asyncio.run(crud.add_instances(catalog, fake_session))
    yield catalog
    folders = asyncio.run(crud.get_folders(fake_session))
    asyncio.run(crud.delete_cls_instances(folders, fake_session))
    products = asyncio.run(crud.get_products(fake_session))
    asyncio.run(crud.delete_cls_instances(products, fake_session))


@pytest.fixture
def fake_retailers(fake_session):
    """Fill database with fake retailers required for price parser tests."""

    retailers = (
        Retailer(name=RetailerName.TAVRIA, home_url=c.TAVRIA_TEST_URL),
    )
    asyncio.run(crud.add_instances(retailers, fake_session))
    yield retailers
    asyncio.run(crud.delete_cls_instances(retailers, fake_session))


@pytest.fixture
def fake_price_lines(fake_session, fake_catalog_db, fake_retailers):
    """Fill database with fake price lines required for price parser tests."""

    lines = (
        # exist on page, exist in base, same price
        PriceLine(product_id=1, retailer_id=1, retail_price=65.90, promo_price=58.90, date_created=date(2023, 1, 1)),
        PriceLine(product_id=2, retailer_id=1, retail_price=74.90, promo_price=None, date_created=date(2023, 1, 1)),
        PriceLine(product_id=3, retailer_id=1, retail_price=77.90, promo_price=None, date_created=date(2023, 1, 1)),
        PriceLine(product_id=4, retailer_id=1, retail_price=89.90, promo_price=None, date_created=date(2023, 1, 1)),
        # exist on page, exist in base, wrong price
        PriceLine(product_id=5, retailer_id=1, retail_price=17.40, promo_price=None, date_created=date(2023, 1, 1)),
        PriceLine(product_id=6, retailer_id=1, retail_price=42.60, promo_price=None, date_created=date(2023, 1, 1)),
        PriceLine(product_id=7, retailer_id=1, retail_price=32.20, promo_price=None, date_created=date(2023, 1, 1)),
        PriceLine(product_id=8, retailer_id=1, retail_price=27.40, promo_price=23.90, date_created=date(2023, 1, 1)),
        # not exist on page, exist in base
        PriceLine(product_id=9, retailer_id=1, retail_price=47.90, promo_price=None, date_created=date(2023, 1, 1)),
        PriceLine(product_id=10, retailer_id=1, retail_price=68.20, promo_price=None, date_created=date(2023, 1, 1)),
        PriceLine(product_id=11, retailer_id=1, retail_price=87.60, promo_price=None, date_created=date(2023, 1, 1)),
        PriceLine(product_id=12, retailer_id=1, retail_price=63.70, promo_price=None, date_created=date(2023, 1, 1)),
    )
    asyncio.run(crud.add_instances(lines, fake_session))
    yield lines
    asyncio.run(crud.delete_cls_instances(lines, fake_session))
