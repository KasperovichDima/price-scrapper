"""Parser test reference values."""
from core.models import PriceLine


ref_actual_folder_names = {
    'Бакалія',
    'Крупи',
    'Гречана крупа',
    'Кукурудзяна крупа',
    'Рис',
    'Протеїнові батончики',
    'Їжа швидкого приготування',
    'Снеки',
    'Чіпси',
}

ref_deprecated_folder_names = {
    'Deprecated folder 1',
    'Deprecated folder 2',
    'Deprecated folder 3',
}

ref_actual_product_names = {
    'Крупа Українська Зірка Гречана 1 кг',
    'Крупа Хуторок Гречана 800 г',
    'Крупа Сквирянка Гречана 800 г',
    'Крупа Сквирянка Гречана 800 г непропарена',
    'Крупа Українська Зірка 800 г Кукурудзяна',
    'Крупа Терра Кукурудзяна 5х80 г',
    'Крупа Моя Країна Кукурудзяна 600 г',
    'Крупа Жменька Кукурудзяна 300 г картон',
    'Рис круглий ваг.',
    'Рис Хуторок 800 г круглий',
    'Рис Трапеза 500 г Басматі пропарений',
    'Рис Хуторок 800 г пропарений',
    'Батончик протеїновий Healthy Meal 40 г з фісташками глазур.',
    'Батончик протеїновий Vale 4Energy 40 г вишня',
    'Батончик протеїновий Vale 40 г полуниця',
    'Батончик Biotech Protein Bar 70 г Strawberry',
    'Локшина Роллтон яєчна 75 г стак. зі смаком Курки по-домашньому',
    'Пюре картопл. Эко 30 г Вершкове',
    'Каша Терра вівсяна з верш. 38 г з абрикосом',
    'Каша Терра 38 г вівсяна з яблуком та корицею',
    "Чіпси '7' 70 г зі смаком сметани та зелені (кор.)",
    'Чіпси Люкс 133 г сир',
    'Чіпси Люкс 71 г бекон',
}

ref_deprecated_product_names = {
    'Deprecated product 1',
    'Deprecated product 2',
    'Deprecated product 3',
    'Deprecated product 4',
}

ref_price_lines = {
    PriceLine(product_id=1, retailer_id=1, retail_price=65.90, promo_price=58.90),  # Крупа Українська Зірка Гречана 1 кг
    PriceLine(product_id=2, retailer_id=1, retail_price=74.90, promo_price=None),  # Крупа Хуторок Гречана 800 г
    PriceLine(product_id=3, retailer_id=1, retail_price=77.90, promo_price=None),  # Крупа Сквирянка Гречана 800 г
    PriceLine(product_id=4, retailer_id=1, retail_price=89.90, promo_price=None),  # Крупа Сквирянка Гречана 800 г непропарена
    PriceLine(product_id=5, retailer_id=1, retail_price=14.90, promo_price=None),  # Крупа Українська Зірка 800 г Кукурудзяна
    PriceLine(product_id=6, retailer_id=1, retail_price=39.80, promo_price=27.60),  # Крупа Терра Кукурудзяна 5х80 г
    PriceLine(product_id=7, retailer_id=1, retail_price=36.00, promo_price=None),  # Крупа Моя Країна Кукурудзяна 600 г
    PriceLine(product_id=8, retailer_id=1, retail_price=25.10, promo_price=None),  # Крупа Жменька Кукурудзяна 300 г картон
    PriceLine(product_id=9, retailer_id=1, retail_price=47.90, promo_price=None),  # Рис круглий ваг.
    PriceLine(product_id=10, retailer_id=1, retail_price=69.40, promo_price=56.90),  # Рис Хуторок 800 г круглий
    PriceLine(product_id=11, retailer_id=1, retail_price=87.60, promo_price=None),  # Рис Трапеза 500 г Басматі пропарений
    PriceLine(product_id=12, retailer_id=1, retail_price=63.70, promo_price=None),  # Рис Хуторок 800 г пропарений
    PriceLine(product_id=13, retailer_id=1, retail_price=45.40, promo_price=None),  # Батончик протеїновий Healthy Meal 40 г з фісташками глазур.
    PriceLine(product_id=14, retailer_id=1, retail_price=16.80, promo_price=None),  # Батончик протеїновий Vale 4Energy 40 г вишня
    PriceLine(product_id=15, retailer_id=1, retail_price=16.80, promo_price=None),  # Батончик протеїновий Vale 40 г полуниця
    PriceLine(product_id=16, retailer_id=1, retail_price=95.60, promo_price=None),  # Батончик Biotech Protein Bar 70 г Strawberry
    PriceLine(product_id=17, retailer_id=1, retail_price=33.80, promo_price=None),  # Локшина Роллтон яєчна 75 г стак. зі смаком Курки по-домашньому
    PriceLine(product_id=18, retailer_id=1, retail_price=12.40, promo_price=None),  # Пюре картопл. Эко 30 г Вершкове
    PriceLine(product_id=19, retailer_id=1, retail_price=13.60, promo_price=None),  # Каша Терра вівсяна з верш. 38 г з абрикосом
    PriceLine(product_id=20, retailer_id=1, retail_price=12.20, promo_price=None),  # Каша Терра 38 г вівсяна з яблуком та корицею
    PriceLine(product_id=21, retailer_id=1, retail_price=18.30, promo_price=None),  # Чіпси '7' 70 г зі смаком сметани та зелені (кор.)
    PriceLine(product_id=22, retailer_id=1, retail_price=38.00, promo_price=None),  # Чіпси Люкс 71 г бекон
    PriceLine(product_id=23, retailer_id=1, retail_price=59.80, promo_price=None),  # Чіпси Люкс 133 г сир
}
