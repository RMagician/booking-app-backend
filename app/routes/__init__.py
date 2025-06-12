"""
Package init for routes module
"""

from app.routes.health import router as health_router

__all__ = ["health_router"]
