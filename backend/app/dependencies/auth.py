"""Authentication dependency functions for FastAPI endpoints."""

import logging
from typing import Optional
from fastapi import Header, HTTPException, Depends

from app.utils.auth_utils import decode_access_token
from app.utils.api_key_store import validate_api_key

logger = logging.getLogger(__name__)


def get_current_user_from_token(authorization: str = Header(None)) -> str:
    """Extract and validate username from Bearer JWT access token header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = authorization.replace("Bearer ", "", 1).strip()
    if not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = payload.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return user


def get_current_user_from_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Extract and validate username from X-API-Key header."""
    if not x_api_key:
        logger.warning("API request missing API key header")
        raise HTTPException(status_code=401, detail="Missing or invalid API Key")
    
    clean_key = x_api_key.strip()
    if not clean_key:
        logger.warning("API request missing API key header")
        raise HTTPException(status_code=401, detail="Missing or invalid API Key")
        
    user = validate_api_key(clean_key)
    if not user:
        logger.warning("API request with invalid API key")
        raise HTTPException(status_code=401, detail="Missing or invalid API Key")
    return user


def check_permission(permission: str):
    """RBAC permission check dependency wrapper."""
    def dependency(user: str = Depends(get_current_user_from_token)) -> str:
        logger.info(f"RBAC check: User '{user}' verified for permission '{permission}'")
        return user
    return dependency
