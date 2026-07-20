USERS = {
    "Heath93": {
        "username": "Heath93",
        "password": "s3cret",
    },
    "test222": {
        "username": "test222",
        "password": "2222222",
    },
}

def get_user(name: str) -> dict:
    if name not in USERS:
        raise KeyError(f"Unknown user: {name}. Add it to config/users.py")
    return USERS[name]