"""API Key repository for hashed key persistence and validation."""

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import logging
import uuid
from typing import Any, List, Optional, Tuple, cast
from sqlalchemy.orm import Session

from app.models.auth_models import DBApiKey, DBUser

logger = logging.getLogger(__name__)


def hash_api_key(raw_key: str) -> str:
    """Compute SHA-256 hex digest of raw API key string."""
    return hashlib.sha256(raw_key.strip().encode("utf-8")).hexdigest()


class ApiKeyRepository:
    """Repository handling DBApiKey CRUD and verification."""

    @staticmethod
    def create_api_key(
        db: Session,
        user_id: int,
        name: str = "Default Key",
        expires_in_days: Optional[int] = 30
    ) -> Tuple[str, DBApiKey]:
        """
        Generate a secure UUID4 API key, hash it using SHA-256, and persist DBApiKey record.
        
        Returns:
            Tuple of (raw_api_key, key_model)
        """
        raw_key = str(uuid.uuid4())
        key_hash = hash_api_key(raw_key)

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=expires_in_days) if expires_in_days else None

        api_key_record = DBApiKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            created_at=now,
            last_used_at=None,
            expires_at=expires_at,
            is_active=True
        )
        db.add(api_key_record)
        db.commit()
        db.refresh(api_key_record)

        logger.info(f"Generated new API key '{name}' for user_id {user_id}")
        return raw_key, api_key_record

    @staticmethod
    def validate_api_key(db: Session, raw_api_key: str) -> Optional[DBUser]:
        """
        Validate incoming raw API key against stored SHA-256 key_hash with constant-time comparison.
        
        Checks:
        1. Key exists in database matching SHA-256 hash.
        2. Key `is_active` status is True.
        3. Key `expires_at` timestamp has not passed.
        4. Associated user `is_active` is True.
        
        Updates `last_used_at` on successful validation.
        """
        clean_key = raw_api_key.strip()
        if not clean_key:
            return None

        computed_hash = hash_api_key(clean_key)
        key_record = db.query(DBApiKey).filter(DBApiKey.key_hash == computed_hash).first()
        if not key_record:
            return None

        rec_hash = str(cast(Any, key_record).key_hash)

        # Constant-time comparison check
        if not hmac.compare_digest(rec_hash, computed_hash):
            return None

        # Check key active state
        if not bool(cast(Any, key_record).is_active):
            logger.warning(f"Validation rejected for revoked API key ID {key_record.id}")
            return None

        # Check expiration date
        now = datetime.now(timezone.utc)
        exp_time = cast(Optional[datetime], cast(Any, key_record).expires_at)
        if exp_time:
            if exp_time.tzinfo is None:
                exp_time = exp_time.replace(tzinfo=timezone.utc)
            if exp_time < now:
                logger.warning(f"Validation rejected for expired API key ID {key_record.id}")
                return None

        # Check associated user active state
        user = cast(Optional[DBUser], cast(Any, key_record).user)
        if not user or not bool(cast(Any, user).is_active):
            return None

        # Rotate last_used_at timestamp
        setattr(key_record, "last_used_at", now)
        db.commit()

        return user

    @staticmethod
    def revoke_api_key(db: Session, key_id: int, user_id: int) -> bool:
        """Deactivate (revoke) an API key record."""
        key_record = db.query(DBApiKey).filter(
            DBApiKey.id == key_id,
            DBApiKey.user_id == user_id
        ).first()
        if not key_record:
            return False

        setattr(key_record, "is_active", False)
        db.commit()
        logger.info(f"Revoked API key ID {key_id} for user_id {user_id}")
        return True

    @staticmethod
    def get_user_api_keys(db: Session, user_id: int) -> List[DBApiKey]:
        """Get all API key records for a user."""
        return db.query(DBApiKey).filter(DBApiKey.user_id == user_id).all()
