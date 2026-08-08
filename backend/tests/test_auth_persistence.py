"""Unit and integration tests for persistent authentication system."""

from datetime import datetime, timedelta, timezone
import pytest
from app.database import SessionLocal
from app.models.auth_models import DBUser, DBApiKey
from app.repositories.user_repository import UserRepository
from app.repositories.api_key_repository import ApiKeyRepository, hash_api_key
from app.utils.user_store import create_user, authenticate_user
from app.utils.api_key_store import generate_api_key, validate_api_key


@pytest.fixture(autouse=True)
def db_session():
    """Provides clean database session for test teardown."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_user_registration_and_authentication(db_session):
    """Verify user registration and authentication via UserRepository."""
    username = "test_sec_user"
    password = "SecPassword123!"

    # Registration
    user = UserRepository.create_user(db_session, username=username, password=password, email="test_sec@dcoy.io")
    assert user is not None
    assert user.username == username
    assert user.email == "test_sec@dcoy.io"
    assert user.is_active is True

    # Duplicate username check
    dup_user = UserRepository.create_user(db_session, username=username, password="NewPassword123!")
    assert dup_user is None

    # Authentication success
    auth_user = UserRepository.authenticate_user(db_session, username=username, password=password)
    assert auth_user is not None
    assert auth_user.id == user.id

    # Authentication failure on wrong password
    bad_auth = UserRepository.authenticate_user(db_session, username=username, password="WrongPassword!")
    assert bad_auth is None


def test_legacy_user_store_wrapper():
    """Verify user_store wrapper functions work seamlessly with database."""
    username = "legacy_test_user"
    password = "LegacyPassword123!"

    # Wrapper registration
    res = create_user(username, password)
    assert res is True

    # Duplicate registration check
    dup_res = create_user(username, password)
    assert dup_res is False

    # Wrapper authentication
    auth_res = authenticate_user(username, password)
    assert auth_res is True

    bad_res = authenticate_user(username, "InvalidPwd")
    assert bad_res is False


def test_api_key_lifecycle_and_hashing(db_session):
    """Verify SHA-256 key hashing, validation, revocation, and expiration logic."""
    username = "apikey_test_user"
    user = UserRepository.create_user(db_session, username=username, password="UserPassword123!")
    assert user is not None

    # Create API key
    raw_key, key_record = ApiKeyRepository.create_api_key(db_session, user_id=user.id, name="Test Key", expires_in_days=7)
    assert raw_key is not None
    assert len(raw_key) > 20
    # Plaintext key should NOT equal key_hash
    assert raw_key != key_record.key_hash
    assert key_record.key_hash == hash_api_key(raw_key)

    # Validate API key
    valid_user = ApiKeyRepository.validate_api_key(db_session, raw_key)
    assert valid_user is not None
    assert valid_user.username == username

    # Verify last_used_at timestamp updated
    db_session.refresh(key_record)
    assert key_record.last_used_at is not None

    # Revoke API key
    rev_res = ApiKeyRepository.revoke_api_key(db_session, key_record.id, user.id)
    assert rev_res is True

    # Revoked key validation should fail
    revoked_val = ApiKeyRepository.validate_api_key(db_session, raw_key)
    assert revoked_val is None


def test_expired_api_key_rejection(db_session):
    """Verify expired API keys are rejected during validation."""
    username = "expired_key_user"
    user = UserRepository.create_user(db_session, username=username, password="UserPassword123!")
    assert user is not None

    # Create key expired in the past
    raw_key, key_record = ApiKeyRepository.create_api_key(db_session, user_id=user.id, name="Expired Key")
    key_record.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.commit()

    val_res = ApiKeyRepository.validate_api_key(db_session, raw_key)
    assert val_res is None


def test_invalid_api_key_rejection(db_session):
    """Verify unknown/invalid raw API keys are rejected."""
    val_res = ApiKeyRepository.validate_api_key(db_session, "invalid-uuid-key-9999")
    assert val_res is None


def test_legacy_api_key_store_wrapper():
    """Verify api_key_store wrapper functions work seamlessly with database."""
    username = "legacy_apikey_user"
    create_user(username, "LegacyPassword123!")

    # Wrapper key generation
    raw_key = generate_api_key(username)
    assert raw_key is not None

    # Wrapper key validation
    validated_username = validate_api_key(raw_key)
    assert validated_username == username

    # Invalid key validation check
    bad_username = validate_api_key("fake-key-string")
    assert bad_username is None


def test_persistence_after_session_restart():
    """Verify database user and API key records persist across session instances."""
    username = "restart_persisted_user"
    password = "PersistPassword123!"

    # Create user and key in first session scope
    db1 = SessionLocal()
    u = UserRepository.create_user(db1, username=username, password=password)
    raw_key, k = ApiKeyRepository.create_api_key(db1, user_id=u.id, name="Persisted Key")
    db1.close()

    # Query user and key in second clean session instance
    db2 = SessionLocal()
    fetched_user = UserRepository.get_by_username(db2, username)
    assert fetched_user is not None
    assert fetched_user.username == username

    valid_user = ApiKeyRepository.validate_api_key(db2, raw_key)
    assert valid_user is not None
    assert valid_user.username == username
    db2.close()
