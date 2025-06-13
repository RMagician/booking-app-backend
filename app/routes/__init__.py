"""
Package init for routes module
"""

from app.routes.health import router as health_router
from app.routes.service import router as service_router

__all__ = ["health_router", "service_router"]
