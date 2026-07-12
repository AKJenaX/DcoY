from datetime import datetime, timezone
from app.utils.auth_utils import hash_password, verify_password

users_db = {}

def create_user(username: str, password: str) -> bool:
    """Create a new user storing password securely using bcrypt."""
    if username in users_db:
        return False
    users_db[username] = {
        "password": hash_password(password),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    return True

def authenticate_user(username: str, password: str) -> bool:
    """Verify password by comparing hash values."""
    if username in users_db:
        hashed = users_db[username].get("password")
        if hashed and verify_password(password, hashed):
            return True
    return False
