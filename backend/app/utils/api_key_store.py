import uuid
from datetime import datetime

api_keys_db = {}

def generate_api_key(user: str) -> str:
    key = str(uuid.uuid4())
    api_keys_db[key] = {
        "user": user,
        "created_at": datetime.utcnow().isoformat()
    }
    return key

def validate_api_key(api_key: str) -> str:
    if api_key in api_keys_db:
        return api_keys_db[api_key]["user"]
    return None
