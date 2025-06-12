"""
Health check and status routes
"""

from typing import Dict
from fastapi import APIRouter, Depends

from app.config import get_settings
from app.database.mongodb import get_database

router = APIRouter(tags=["status"])


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint that returns the status of the API
    """
    return {"status": "healthy", "version": "0.1.0"}


@router.get("/status")
async def status(settings=Depends(get_settings)) -> Dict[str, str]:
    """
    Returns detailed status of the API and its dependencies
    """
    db = get_database()

    try:
        # Check MongoDB connection
        await db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "online",
        "environment": settings.ENV,
        "database": db_status,
        "version": "0.1.0",
    }
