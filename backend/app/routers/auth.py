"""Authentication and API Key management router."""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.api_key_repository import ApiKeyRepository
from app.utils.auth_utils import create_access_token

logger = logging.getLogger(__name__)

router = APIRouter()


class AuthRequest(BaseModel):
    username: str
    password: str


@router.post(
    "/register",
    summary="Register New User Account",
    description="Registers a new user account with bcrypt password hashing in database."
)
def register_user(body: AuthRequest, db: Session = Depends(get_db)) -> Dict[str, str]:
    logger.info(f"POST /register - New user: {body.username}")
    user = UserRepository.create_user(db, username=body.username, password=body.password)
    if user:
        logger.info(f"User {body.username} registered successfully")
        return {"message": "User created successfully"}
    logger.warning(f"Registration failed for {body.username}: user already exists")
    raise HTTPException(status_code=400, detail="User already exists")


@router.post(
    "/login",
    summary="User Login",
    description="Authenticates user credentials against database and returns a Bearer JWT access token."
)
def login_user(body: AuthRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    logger.info(f"POST /login - User: {body.username}")
    user = UserRepository.authenticate_user(db, username=body.username, password=body.password)
    if user:
        token = create_access_token({"user": user.username})
        logger.info(f"User {user.username} logged in successfully")
        return {
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer",
            "user": user.username,
        }
    logger.warning(f"Login failed for {body.username}: invalid credentials")
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post(
    "/generate-api-key",
    summary="Generate API Key",
    description="Generates and persists a SHA-256 hashed API key record, returning the un-hashed key once."
)
def generate_key_endpoint(body: AuthRequest, db: Session = Depends(get_db)) -> Dict[str, str]:
    username = body.username.strip().lower()
    password = body.password.strip()
    logger.info(f"POST /generate-api-key - User: {username}")

    user = UserRepository.authenticate_user(db, username=username, password=password)
    if not user:
        logger.warning(f"API key generation failed for {username}: invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    raw_key, key_record = ApiKeyRepository.create_api_key(db, user_id=int(getattr(user, "id")), name="Generated API Key")
    logger.info(f"API key generated for user: {username} (Key ID: {key_record.id})")
    return {
        "api_key": raw_key,
        "user": username
    }
