"""User repository for database user account persistence."""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, Optional, cast
from sqlalchemy.orm import Session

from app.models.auth_models import DBUser
from app.utils.auth_utils import hash_password, verify_password

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository handling DBUser CRUD operations."""

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        password: str,
        email: Optional[str] = None,
        role: str = "User"
    ) -> Optional[DBUser]:
        """Create a new DBUser record with bcrypt password hashing."""
        clean_username = username.strip().lower()
        if not clean_username:
            return None

        # Check existing username
        existing_user = db.query(DBUser).filter(DBUser.username == clean_username).first()
        if existing_user:
            logger.warning(f"User creation failed: username '{clean_username}' already exists")
            return None

        # Check existing email if provided
        if email:
            clean_email = email.strip().lower()
            existing_email = db.query(DBUser).filter(DBUser.email == clean_email).first()
            if existing_email:
                logger.warning(f"User creation failed: email '{clean_email}' already exists")
                return None
        else:
            clean_email = None

        user = DBUser(
            username=clean_username,
            email=clean_email,
            password_hash=hash_password(password),
            role=role,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"User '{clean_username}' created successfully in database (ID: {user.id})")
        return user

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[DBUser]:
        """Retrieve user record by username."""
        clean_username = username.strip().lower()
        return db.query(DBUser).filter(DBUser.username == clean_username).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[DBUser]:
        """Retrieve user record by email."""
        clean_email = email.strip().lower()
        return db.query(DBUser).filter(DBUser.email == clean_email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[DBUser]:
        """Retrieve user record by ID."""
        return db.query(DBUser).filter(DBUser.id == user_id).first()

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[DBUser]:
        """Verify user credentials against stored bcrypt password hash."""
        user = UserRepository.get_by_username(db, username)
        if not user or not bool(cast(Any, user).is_active):
            return None
        if verify_password(password, str(cast(Any, user).password_hash)):
            return user
        return None

    @staticmethod
    def update_user(db: Session, user_id: int, updates: Dict[str, Any]) -> Optional[DBUser]:
        """Update DBUser record fields."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None
        for key, val in updates.items():
            if key == "password":
                setattr(user, "password_hash", hash_password(val))
            elif hasattr(user, key):
                setattr(user, key, val)
        setattr(user, "updated_at", datetime.now(timezone.utc))
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete DBUser record."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True
