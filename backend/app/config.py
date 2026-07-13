"""Platform Settings and Configurations Manager."""

import os
import secrets
from typing import Optional


class Settings:
    """Central settings manager parsing environment variables with secure production validation."""

    def __init__(self):
        self.APP_NAME: str = os.getenv("APP_NAME", "DcoY")
        
        # Parse DEBUG: default to True
        debug_env = os.getenv("DEBUG", "True").lower()
        self.DEBUG: bool = debug_env == "true" or debug_env == "1"

        # Parse ENV
        self.ENV: str = os.getenv("ENV", "development").lower()

        # Parse SECRET_KEY (JWT signing secret)
        raw_key = os.getenv("SECRET_KEY", "")
        
        # Security validation checks
        if not self.DEBUG:  # Production Mode (DEBUG=False)
            if not raw_key:
                raise ValueError("CRITICAL SECURITY ERROR: SECRET_KEY is missing or empty in production mode!")
            if len(raw_key) < 32:
                raise ValueError("SECRET_KEY is missing, too short (< 32 chars) in production mode!")
            self.SECRET_KEY = raw_key
        else:  # Development Mode (DEBUG=True)
            if not raw_key or len(raw_key) < 32:
                # Weak or missing key triggers secure auto-generation
                self.SECRET_KEY = secrets.token_hex(32)
            else:
                self.SECRET_KEY = raw_key

        self.JWT_ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

        # Database Settings
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///backend/dcoy.db")

        # LLM Reasoning Settings
        self.LLM_ENABLED: bool = os.getenv("LLM_ENABLED", "True").lower() == "true"
        self.LLM_HOST: str = os.getenv("LLM_HOST", "http://127.0.0.1:11434")
        self.LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3")
        self.LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "2.0"))
        self.LLM_HEALTH_CHECK_INTERVAL: float = float(os.getenv("LLM_HEALTH_CHECK_INTERVAL", "60.0"))
        self.LLM_RETRY_INTERVAL: float = float(os.getenv("LLM_RETRY_INTERVAL", "30.0"))
        self.LLM_FAILURE_THRESHOLD: int = int(os.getenv("LLM_FAILURE_THRESHOLD", "3"))

        # Observability Settings
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.LOG_FORMAT_JSON: bool = os.getenv("LOG_FORMAT_JSON", "false").lower() == "true"

    def validate(self):
        """Validate safety parameters, raising warnings for insecure keys in production."""
        if not self.DEBUG:
            if not self.SECRET_KEY:
                raise ValueError("CRITICAL SECURITY ERROR: SECRET_KEY is missing or empty in production mode!")
            if len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY is missing, too short (< 32 chars) in production mode!")


settings = Settings()
