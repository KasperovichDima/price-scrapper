"""Authentication schemas exmples."""
from project_typing import UserType


user_create = {
    "example": {
        "first_name": "John",
        "last_name": "Travolta",
        "email": "john@travolta.com",
        "password": "JohnTravolta1954"
    }
}


user_scheme = {
    "example": {
        "first_name": "John",
        "last_name": "Travolta",
        "email": "john@travolta.com",
        "id": 17,
        "is_active": True,
        "type": UserType.USER,
    }
}
