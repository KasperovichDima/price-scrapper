"""Reference json responses for unit tests."""
from .tavria_tree_builder_result import tavria_tree_builder_result  # noqa: F401 E501


get_content_ok_ref = {
    'folders': [],
    'products': [
        {'id': 1, 'name': 'Beer Chernigovskoe 0,5', 'parent_id': 1, 'type': 1, 'prime_cost': 23.5},  # noqa: E501
        {'id': 2, 'name': 'Vine Cartuli Vazi 0,7', 'parent_id': 1, 'type': 1, 'prime_cost': 58.15},  # noqa: E501
        {'id': 3, 'name': 'Vodka Finlandia 0,7', 'parent_id': 1, 'type': 1, 'prime_cost': 115.96}]  # noqa: E501
    }


add_ok_ref = {
    'folders': [
        {'id': 2, 'name': 'Grocery', 'parent_id': None, 'type': 2},
        {'id': 3, 'name': 'Milk', 'parent_id': None, 'type': 2}
        ],
    'products': [
        {'id': 1, 'name': 'Beer Chernigovskoe 0,5', 'parent_id': 1, 'type': 1},
        {'id': 5, 'name': 'Chips 500 gr', 'parent_id': 2, 'type': 1},
        {'id': 6, 'name': 'Sugar 1kg', 'parent_id': 2, 'type': 1},
        {'id': 4, 'name': 'Sunflower Oil 1l', 'parent_id': 2, 'type': 1},
        {'id': 2, 'name': 'Vine Cartuli Vazi 0,7', 'parent_id': 1, 'type': 1},
        {'id': 3, 'name': 'Vodka Finlandia 0,7', 'parent_id': 1, 'type': 1}
        ],
    'retailers': [
        {'id': 2, 'name': 'Silpo'},
        {'id': 1, 'name': 'Tavria'}
        ]
}

remove_items_ok_ref = {
    'folders': [{'id': 2, 'name': 'Grocery', 'parent_id': None, 'type': 2}],
    'products': [
        {'id': 1, 'name': 'Beer Chernigovskoe 0,5', 'parent_id': 1, 'type': 1},
        {'id': 5, 'name': 'Chips 500 gr', 'parent_id': 2, 'type': 1},
        {'id': 6, 'name': 'Sugar 1kg', 'parent_id': 2, 'type': 1},
        {'id': 2, 'name': 'Vine Cartuli Vazi 0,7', 'parent_id': 1, 'type': 1}
        ],
    'retailers': [{'id': 2, 'name': 'Silpo'}]
}

get_report_ok_ref = {
    'header': {
        'name': 'just a fake report',
        'note': 'just a fake note',
        'time_created': '2022-12-10T15:42:32.373798',
        'user_name': 'Dima Kasperovich'
        },
    'folders': [
        {'id': 2, 'name': 'Grocery', 'parent_id': None, 'type': 2},
        {'id': 3, 'name': 'Milk', 'parent_id': None, 'type': 2}
        ],
    'products': [
        {'id': 1, 'name': 'Beer Chernigovskoe 0,5', 'parent_id': 1, 'type': 1, 'prime_cost': 23.5},  # noqa: E501
        {'id': 5, 'name': 'Chips 500 gr', 'parent_id': 2, 'type': 1, 'prime_cost': 15.2},  # noqa: E501
        {'id': 6, 'name': 'Sugar 1kg', 'parent_id': 2, 'type': 1, 'prime_cost': 9.99},  # noqa: E501
        {'id': 4, 'name': 'Sunflower Oil 1l', 'parent_id': 2, 'type': 1, 'prime_cost': 20.99},  # noqa: E501
        {'id': 2, 'name': 'Vine Cartuli Vazi 0,7', 'parent_id': 1, 'type': 1, 'prime_cost': 58.15},  # noqa: E501
        {'id': 3, 'name': 'Vodka Finlandia 0,7', 'parent_id': 1, 'type': 1, 'prime_cost': 115.96}],  # noqa: E501
    'retailers': [
        {'id': 2, 'name': 'Silpo'},
        {'id': 1, 'name': 'Tavria'}
        ],
    'content': [
        {'product_id': 1, 'retailer_id': 1, 'retail_price': 50.0, 'promo_price': 40.0},  # noqa: E501
        {'product_id': 1, 'retailer_id': 2, 'retail_price': 51.0, 'promo_price': 41.0},  # noqa: E501
        {'product_id': 2, 'retailer_id': 1, 'retail_price': 53.0, 'promo_price': 43.0},  # noqa: E501
        {'product_id': 2, 'retailer_id': 2, 'retail_price': 54.0, 'promo_price': 44.0},  # noqa: E501
        {'product_id': 3, 'retailer_id': 1, 'retail_price': 56.0, 'promo_price': 46.0},  # noqa: E501
        {'product_id': 3, 'retailer_id': 2, 'retail_price': 57.0, 'promo_price': 47.0},  # noqa: E501
        {'product_id': 4, 'retailer_id': 1, 'retail_price': 59.0, 'promo_price': 49.0},  # noqa: E501
        {'product_id': 4, 'retailer_id': 2, 'retail_price': 60.0, 'promo_price': 50.0},  # noqa: E501
        {'product_id': 5, 'retailer_id': 1, 'retail_price': 62.0, 'promo_price': 52.0},  # noqa: E501
        {'product_id': 5, 'retailer_id': 2, 'retail_price': 63.0, 'promo_price': 53.0},  # noqa: E501
        {'product_id': 6, 'retailer_id': 1, 'retail_price': 65.0, 'promo_price': 55.0},  # noqa: E501
        {'product_id': 6, 'retailer_id': 2, 'retail_price': 66.0, 'promo_price': 56.0}  # noqa: E501
        ]
    }


