"""Application configuration loaded from environment variables."""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


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


settings = Settings()
