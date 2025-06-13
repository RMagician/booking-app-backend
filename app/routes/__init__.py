"""
Package init for routes module
"""

from .health import router as health_router
from .service import router as service_router
from .booking import router as booking_router

__all__ = ["health_router", "service_router", "booking_router"]
