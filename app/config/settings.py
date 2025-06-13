"""
Configuration module for loading environment variables
"""

import os
from functools import lru_cache
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv(encoding="utf-8")


class Settings(BaseModel):
    """Application settings loaded from environment variables"""

    # Environment
    ENV: str = Field(default=os.getenv("ENV", "development"))

    # MongoDB
    MONGODB_URI: str = Field(
        default=os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    )
    MONGODB_DB_NAME: str = Field(
        default=os.getenv("MONGODB_DB_NAME", "booking_app")
    )

    # API
    API_PREFIX: str = Field(default=os.getenv("API_PREFIX", "/api"))


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
