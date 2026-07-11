import pytest
import time
import os
from unittest.mock import patch
from jose import jwt, ExpiredSignatureError
from app.utils.auth_utils import hash_password, verify_password, create_access_token, decode_access_token
from app.config import Settings, settings

def test_bcrypt_password_hashing():
    """Verify that password hashing correctly generates bcrypt hashes and validates matches."""
    plain = "operator_password_123"
    hashed = hash_password(plain)
    
    # Assert hash is stored differently than cleartext
    assert hashed != plain
    assert hashed.startswith("$2b$")  # bcrypt prefix
    
    # Assert correct verification matches
    assert verify_password(plain, hashed) is True
    
    # Assert incorrect credentials verification fails
    assert verify_password("wrong_password", hashed) is False

def test_jwt_tampering():
    """Tampering with token payload signature must cause validation failure."""
    token = create_access_token({"user": "malicious_operator"})
    
    # Tamper with the signature suffix (last characters of JWT)
    parts = token.split(".")
    assert len(parts) == 3
    tampered_signature = parts[2][:-4] + "AAAA"  # corrupt signature
    tampered_token = f"{parts[0]}.{parts[1]}.{tampered_signature}"
    
    decoded = decode_access_token(tampered_token)
    assert decoded is None

def test_jwt_expiration():
    """Expired access token signature must fail decoding."""
    # Temporarily force expiration of ACCESS_TOKEN_EXPIRE_MINUTES to -5 minutes
    with patch("app.config.settings.ACCESS_TOKEN_EXPIRE_MINUTES", -5):
        token = create_access_token({"user": "expired_operator"})
        decoded = decode_access_token(token)
        assert decoded is None

def test_startup_configuration_validations_dev():
    """In development mode (DEBUG=True), a weak SECRET_KEY triggers fallback auto-generation."""
    env_vars = {
        "APP_NAME": "DcoY",
        "DEBUG": "True",
        "SECRET_KEY": "dcoy_secret_key"  # Weak default key
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        # Should initialize successfully and auto-generate a secure random hex key
        dev_settings = Settings()
        assert dev_settings.SECRET_KEY is not None
        assert dev_settings.SECRET_KEY != "dcoy_secret_key"
        assert len(dev_settings.SECRET_KEY) >= 64  # secrets.token_hex(32) is 64 chars

def test_startup_configuration_validations_prod_missing():
    """In production mode (DEBUG=False), missing SECRET_KEY must raise ValueError on start."""
    env_vars = {
        "APP_NAME": "DcoY",
        "DEBUG": "False",
        "SECRET_KEY": ""  # Missing key
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        with pytest.raises(ValueError) as exc:
            Settings()
        assert "CRITICAL SECURITY ERROR" in str(exc.value)

def test_startup_configuration_validations_prod_weak():
    """In production mode (DEBUG=False), a weak SECRET_KEY must raise ValueError on start."""
    env_vars = {
        "APP_NAME": "DcoY",
        "DEBUG": "False",
        "SECRET_KEY": "too_short"  # Too short (< 32 chars)
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        with pytest.raises(ValueError) as exc:
            Settings()
        assert "SECRET_KEY is missing, too short" in str(exc.value)
