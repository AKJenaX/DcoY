"""CORS middleware configuration."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors_middleware(app: FastAPI) -> None:
    """Configure CORS middleware on FastAPI instance."""
    custom_origins = os.getenv("ALLOWED_ORIGINS", "")
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "https://dcoy.pages.dev",
        "https://dcoy-9n8n.onrender.com",
    ]
    if custom_origins:
        allowed_origins.extend([o.strip() for o in custom_origins.split(",") if o.strip()])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=r"https://.*\.pages\.dev",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
