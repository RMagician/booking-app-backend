"""
Schemas module initialization
"""

from app.schemas.service import (
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
    PaginatedServiceRead,  # Ensure this is PaginatedServiceRead
)

from app.schemas.booking import (
    BookingCreate,
    BookingRead,
    BookingUpdate,
    PaginatedBookingRead,  # Ensure this is PaginatedBookingRead
    BookingStatusUpdate,
)

__all__ = [
    "ServiceCreate",
    "ServiceRead",
    "ServiceUpdate",
    "PaginatedServiceRead",  # Ensure this is PaginatedServiceRead
    "BookingCreate",
    "BookingRead",
    "BookingUpdate",
    "PaginatedBookingRead",  # Ensure this is PaginatedBookingRead
    "BookingStatusUpdate",
]
