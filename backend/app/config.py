"""Application configuration loaded from environment variables."""

import os
import secrets
import logging
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _parse_bool(value: Optional[str], *, default: bool = False) -> bool:
    """Return True if the env value looks like a boolean true."""
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in ("true", "1", "yes")


class Settings:
    """Application settings read from the process environment."""

    def __init__(self) -> None:
        self.APP_NAME: str = os.getenv("APP_NAME", "DcoY")
        self.DEBUG: bool = _parse_bool(os.getenv("DEBUG"), default=False)
        self.LLM_ENABLED: bool = _parse_bool(os.getenv("LLM_ENABLED"), default=True)
        self.LLM_HOST: str = os.getenv("LLM_HOST", "http://127.0.0.1:11434").rstrip("/")
        self.LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3")
        self.LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "2.0"))
        self.LLM_HEALTH_CHECK_INTERVAL: float = float(os.getenv("LLM_HEALTH_CHECK_INTERVAL", "60.0"))
        self.LLM_RETRY_INTERVAL: float = float(os.getenv("LLM_RETRY_INTERVAL", "30.0"))
        self.LLM_FAILURE_THRESHOLD: int = int(os.getenv("LLM_FAILURE_THRESHOLD", "3"))

        # JWT Configuration Settings
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

        # Load and Validate SECRET_KEY
        env_secret = os.getenv("SECRET_KEY")
        is_prod = not self.DEBUG
        
        insecure_keys = (
            "dcoy_secret_key",
            "generate_a_secure_random_key_here_for_prod_use",
            "secret",
            "default",
            "key",
        )
        
        is_insecure = False
        if env_secret:
            clean_secret = env_secret.strip()
            if len(clean_secret) < 32 or clean_secret.lower() in insecure_keys:
                is_insecure = True
        else:
            is_insecure = True

        if is_insecure:
            if is_prod:
                raise ValueError(
                    "CRITICAL SECURITY ERROR: SECRET_KEY is missing, too short (<32 characters), or insecure. "
                    "In production mode (DEBUG=False), a strong SECRET_KEY must be provided in the environment."
                )
            else:
                logger.warning(
                    "WARNING: SECRET_KEY is missing or insecure. "
                    "Generating a temporary secure random key for development environment."
                )
                self.SECRET_KEY: str = secrets.token_hex(32)
        else:
            self.SECRET_KEY: str = env_secret.strip()


settings = Settings()
