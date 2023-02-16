"""Request test reference values."""


add_request_ok_ref = {
    'folders': [
        {'id': 2, 'name': 'Grocery', 'parent_id': None},
        {'id': 3, 'name': 'Milk', 'parent_id': None}
    ],
    'products': [
        {'id': 1, 'name': 'Beer Chernigovskoe 0,5', 'parent_id': 1},  # noqa: E501
        {'id': 5, 'name': 'Chips 500 gr', 'parent_id': 2,},
        {'id': 6, 'name': 'Sugar 1kg', 'parent_id': 2},
        {'id': 4, 'name': 'Sunflower Oil 1l', 'parent_id': 2},
        {'id': 2, 'name': 'Vine Cartuli Vazi 0,7', 'parent_id': 1},  # noqa: E501
        {'id': 3, 'name': 'Vodka Finlandia 0,7', 'parent_id': 1}
    ],
    'retailers': [
        {'id': 2, 'name': 'SILPO'},
        {'id': 1, 'name': 'TAVRIA'}
    ]
}

remove_items_ok_ref = {
    'folders': [
        {'id': 2, 'name': 'Grocery', 'parent_id': None},
    ],
    'products': [
        {'id': 1, 'name': 'Beer Chernigovskoe 0,5', 'parent_id': 1},  # noqa: E501
        {'id': 5, 'name': 'Chips 500 gr', 'parent_id': 2,},
        {'id': 6, 'name': 'Sugar 1kg', 'parent_id': 2},
        {'id': 2, 'name': 'Vine Cartuli Vazi 0,7', 'parent_id': 1},  # noqa: E501
    ],
    'retailers': [
        {'id': 2, 'name': 'SILPO'},
    ]
}
