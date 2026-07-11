import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.live_store import clear_events
from app.utils.feedback_store import feedback_db
from app.utils.api_key_store import api_keys_db
from app.utils.user_store import users_db

@pytest.fixture(autouse=True)
def clean_stores():
    """Clear memory store data structures between test cases."""
    clear_events()
    feedback_db.clear()
    api_keys_db.clear()
    users_db.clear()
    yield


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client
