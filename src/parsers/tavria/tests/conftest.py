"""Parser conftest."""
from datetime import date

from catalog.models import BaseCatalogElement, Folder, Product

from core.models import PriceLine

import crud

from database import TestSession

import pytest_asyncio

from retailer.models import Retailer
from retailer.retailer_typing import RetailerName

from . import constants as c


@pytest_asyncio.fixture
async def fake_catalog_db():
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
        Product(name="Крупа Українська Зірка Гречана 1 кг", parent_id=4, prime_cost=49.93),  # noqa: E501  1
        Product(name="Крупа Хуторок Гречана 800 г", parent_id=4, prime_cost=59.98),  # noqa: E501  2
        Product(name="Крупа Сквирянка Гречана 800 г", parent_id=4, prime_cost=62.15),  # noqa: E501  3
        Product(name="Крупа Сквирянка Гречана 800 г непропарена", parent_id=4, prime_cost=65.75),  # noqa: E501  4
        Product(name="Крупа Українська Зірка 800 г Кукурудзяна", parent_id=5, prime_cost=12.42),  # noqa: E501  5
        Product(name="Крупа Терра Кукурудзяна 5х80 г", parent_id=5, prime_cost=27.68, deprecated=True),  # noqa: E501  6
        Product(name="Крупа Моя Країна Кукурудзяна 600 г", parent_id=5, prime_cost=28.63),  # noqa: E501  7
        Product(name="Крупа Жменька Кукурудзяна 300 г картон", parent_id=5, prime_cost=17.21),  # noqa: E501  8
        Product(name="Рис круглий ваг.", parent_id=6, prime_cost=34.85), #  9
        Product(name="Рис Хуторок 800 г круглий", parent_id=6, prime_cost=57.14),  # noqa: E501  10
        Product(name="Рис Трапеза 500 г Басматі пропарений", parent_id=6, prime_cost=77.11),  # noqa: E501  11
        Product(name="Рис Хуторок 800 г пропарений", parent_id=6, prime_cost=60.32),  # noqa: E501  12
        Product(name="Батончик протеїновий Healthy Meal 40 г з фісташками глазур.", parent_id=7, prime_cost=37.89),  # noqa: E501  13
        Product(name="Батончик протеїновий Vale 4Energy 40 г вишня", parent_id=7, prime_cost=12.47),  # noqa: E501  14
        Product(name="Батончик протеїновий Vale 40 г полуниця", parent_id=7, prime_cost=12.47),  # noqa: E501  15
        Product(name="Батончик Biotech Protein Bar 70 г Strawberry", parent_id=7, prime_cost=74.58),  # noqa: E501  16
        Product(name="Локшина Роллтон яєчна 75 г стак. зі смаком Курки по-домашньому", parent_id=8, prime_cost=22.10),  # noqa: E501  17
        Product(name="Пюре картопл. Эко 30 г Вершкове", parent_id=8, prime_cost=8.41),  # noqa: E501  18
        Product(name="Каша Терра вівсяна з верш. 38 г з абрикосом", parent_id=8, prime_cost=5.65),  # noqa: E501  19
        Product(name="Каша Терра 38 г вівсяна з яблуком та корицею", parent_id=8, prime_cost=5.65),  # noqa: E501  20
        #  Testing to create not existing in db products and get their prices by one async session  # noqa: E501

        # Product(name="Чіпси '7' 70 г зі смаком сметани та зелені (кор.)", parent_id=9, prime_cost=15.00),  # noqa: E501  25
        # Product(name="Чіпси Люкс 71 г бекон", parent_id=9, prime_cost=31.15),  26
        # Product(name="Чіпси Люкс 133 г сир", parent_id=9, prime_cost=45.25),  27

        #  Deprecated products:
        Product(name="Deprecated product 1", parent_id=4, prime_cost=100),  # 21
        Product(name="Deprecated product 2", parent_id=4, prime_cost=110),  # 22
        Product(name="Deprecated product 3", parent_id=5, prime_cost=120),  # 23
        Product(name="Deprecated product 4", parent_id=5, prime_cost=130),  # 24
    )
    async with TestSession() as test_session:
        await crud.add_instances(catalog, test_session)
        await test_session.commit()
        yield catalog
        folders = await crud.get_folders(test_session)
        await crud.delete_cls_instances(folders, test_session)
        products = await crud.get_products(test_session)
        await crud.delete_cls_instances(products, test_session)
        await test_session.commit()


@pytest_asyncio.fixture
async def fake_retailers():
    """Fill database with fake retailers required for price parser tests."""

    retailers = (
        Retailer(name=RetailerName.TAVRIA, home_url=c.TAVRIA_TEST_URL),
    )
    async with TestSession() as test_session: 
        await crud.add_instances(retailers, test_session)
        await test_session.commit()
        yield retailers
        await crud.delete_cls_instances(retailers, test_session)
        await test_session.commit()


@pytest_asyncio.fixture
async def fake_price_lines(fake_catalog_db, fake_retailers):
    """Fill database with fake price lines required for price parser tests."""

    lines = (
        # exist on page, exist in base, same price
        PriceLine(product_id=1, retailer_id=1, retail_price=65.90, promo_price=58.90, date_created=date(2023, 1, 1)),  # Крупа Українська Зірка Гречана 1 кг
        PriceLine(product_id=2, retailer_id=1, retail_price=74.90, promo_price=None, date_created=date(2023, 1, 1)),  # Крупа Хуторок Гречана 800 г
        PriceLine(product_id=3, retailer_id=1, retail_price=77.90, promo_price=None, date_created=date(2023, 1, 1)),  # Крупа Сквирянка Гречана 800 г
        PriceLine(product_id=4, retailer_id=1, retail_price=89.90, promo_price=None, date_created=date(2023, 1, 1)),  # Крупа Сквирянка Гречана 800 г непропарена
        # exist on page, exist in base, wrong price
        PriceLine(product_id=5, retailer_id=1, retail_price=17.40, promo_price=None, date_created=date(2023, 1, 1)),  # Крупа Українська Зірка 800 г Кукурудзяна
        PriceLine(product_id=6, retailer_id=1, retail_price=42.60, promo_price=None, date_created=date(2023, 1, 1)),  # Крупа Терра Кукурудзяна 5х80 г
        PriceLine(product_id=7, retailer_id=1, retail_price=32.20, promo_price=None, date_created=date(2023, 1, 1)),  # Крупа Моя Країна Кукурудзяна 600 г
        PriceLine(product_id=8, retailer_id=1, retail_price=27.40, promo_price=23.90, date_created=date(2023, 1, 1)),  # Крупа Жменька Кукурудзяна 300 г картон
        # not exist on page, exist in base
        PriceLine(product_id=9, retailer_id=1, retail_price=47.90, promo_price=None, date_created=date(2023, 1, 1)),  # Рис круглий ваг.
        PriceLine(product_id=10, retailer_id=1, retail_price=68.20, promo_price=None, date_created=date(2023, 1, 1)),  # Рис Хуторок 800 г круглий
        PriceLine(product_id=11, retailer_id=1, retail_price=87.60, promo_price=None, date_created=date(2023, 1, 1)),  # Рис Трапеза 500 г Басматі пропарений
        PriceLine(product_id=12, retailer_id=1, retail_price=63.70, promo_price=None, date_created=date(2023, 1, 1)),  # Рис Хуторок 800 г пропарений
    )
    async with TestSession() as test_session:
        await crud.add_instances(lines, test_session)
        await test_session.commit()
        yield lines
        await crud.delete_cls_instances(lines, test_session)
        await test_session.commit()
