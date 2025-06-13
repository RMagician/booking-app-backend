"""
Schemas module initialization
"""

from app.schemas.service import (
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
    ServiceList,
)

from app.schemas.booking import (
    BookingCreate,
    BookingRead,
    BookingUpdate,
    BookingList,
    BookingStatusUpdate,
)

__all__ = [
    "ServiceCreate",
    "ServiceRead",
    "ServiceUpdate",
    "ServiceList",
    "BookingCreate",
    "BookingRead",
    "BookingUpdate",
    "BookingList",
    "BookingStatusUpdate",
]
