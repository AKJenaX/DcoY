from datetime import datetime

users_db = {}

def create_user(username: str, password: str) -> bool:
    if username in users_db:
        return False
    users_db[username] = {
        "password": password,
        "created_at": datetime.utcnow().isoformat()
    }
    return True

def authenticate_user(username: str, password: str) -> bool:
    if username in users_db:
        if users_db[username].get("password") == password:
            return True
    return False
