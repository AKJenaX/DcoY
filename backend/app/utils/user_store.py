"""User store wrapper delegating to database UserRepository for backward compatibility."""

import logging
from app.database import SessionLocal
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

# Legacy in-memory dictionary export preserved for backward compatibility & test fixtures
users_db = {}


def create_user(username: str, password: str) -> bool:
    """Create a new user storing password securely using bcrypt via UserRepository."""
    db = SessionLocal()
    try:
        user = UserRepository.create_user(db, username=username, password=password)
        return user is not None
    finally:
        db.close()


def authenticate_user(username: str, password: str) -> bool:
    """Verify password by comparing hash values via UserRepository."""
    db = SessionLocal()
    try:
        user = UserRepository.authenticate_user(db, username=username, password=password)
        return user is not None
    finally:
        db.close()
