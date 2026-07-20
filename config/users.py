USERS = {
    "Heath93": "s3cret",
    "test222": "2222222",
}

def get_password_user(name: str) -> str:
    if name not in USERS:
        raise KeyError(f"Unknown user: {name}. Add it to config/users.py")
    return USERS[name]