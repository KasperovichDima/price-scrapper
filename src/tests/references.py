"""Reference json responses for unit tests."""


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
