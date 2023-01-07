"""Request test reference values."""


add_request_ok_ref = {
    'folders': [
        {'id': 2, 'name': 'Grocery', 'parent_id': None, 'el_type': 1},
        {'id': 3, 'name': 'Milk', 'parent_id': None, 'el_type': 1}
    ],
    'products': [
        {'id': 1, 'name': 'Beer Chernigovskoe 0,5', 'parent_id': 1, 'el_type': 4},
        {'id': 5, 'name': 'Chips 500 gr', 'parent_id': 2, 'el_type': 4},
        {'id': 6, 'name': 'Sugar 1kg', 'parent_id': 2, 'el_type': 4},
        {'id': 4, 'name': 'Sunflower Oil 1l', 'parent_id': 2, 'el_type': 4},
        {'id': 2, 'name': 'Vine Cartuli Vazi 0,7', 'parent_id': 1, 'el_type': 4},
        {'id': 3, 'name': 'Vodka Finlandia 0,7', 'parent_id': 1, 'el_type': 4}
    ],
    'retailers': [
        {'id': 2, 'name': 'Silpo'},
        {'id': 1, 'name': 'Tavria'}
    ]
}


remove_items_ok_ref = {
    'folders': [
        {'id': 2, 'name': 'Grocery', 'parent_id': None, 'el_type': 1},
    ],
    'products': [
        {'id': 1, 'name': 'Beer Chernigovskoe 0,5', 'parent_id': 1, 'el_type': 4},
        {'id': 5, 'name': 'Chips 500 gr', 'parent_id': 2, 'el_type': 4},
        {'id': 6, 'name': 'Sugar 1kg', 'parent_id': 2, 'el_type': 4},
        {'id': 2, 'name': 'Vine Cartuli Vazi 0,7', 'parent_id': 1, 'el_type': 4},
    ],
    'retailers': [
        {'id': 2, 'name': 'Silpo'},
    ]
}