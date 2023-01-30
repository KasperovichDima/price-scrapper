"""Catalog schemas exmples."""
from project_typing import ElType


folder_content = {
    "example": {
        "folders": {
            "id": 23,
            "name": "Гречана крупа",
            "parent_id": 5,
            "el_type": ElType.GROUP
        },
        "products": {
            "id": 554,
            "name": "Крупа Хуторок Гречана 800 г",
            "parent_id": 23,
            "el_type": ElType.PRODUCT
        }
    }
}
