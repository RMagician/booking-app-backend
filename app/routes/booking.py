"""
Booking API routes module
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status

from app.repositories.booking_repository import BookingRepository
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingRead,
    PaginatedBookingRead,  # Ensure this is PaginatedBookingRead
    BookingStatusUpdate,
)
from app.models.booking import BookingStatus

# Define the router with the "bookings" tag
router = APIRouter(tags=["bookings"])


@router.get("/bookings", response_model=PaginatedBookingRead)
async def list_bookings(
    skip: int = Query(0, ge=0, description="Number of bookings to skip"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of bookings to return"
    ),
    sort_by: str = Query("date", description="Field to sort by"),
    sort_direction: int = Query(
        1, ge=-1, le=1, description="Sort direction (1=asc, -1=desc)"
    ),
    status: Optional[BookingStatus] = Query(
        None, description="Filter by booking status"
    ),
    date_from: Optional[datetime] = Query(
        None, description="Filter bookings from this date (inclusive)"
    ),
    date_to: Optional[datetime] = Query(
        None, description="Filter bookings until this date (inclusive)"
    ),
    service_id: Optional[str] = Query(
        None, description="Filter bookings by service ID"
    ),
    customer_name: Optional[str] = Query(
        None, description="Search bookings by customer name"
    ),
    booking_repo: BookingRepository = Depends(lambda: BookingRepository()),
) -> PaginatedBookingRead:
    """
    List all bookings with pagination, sorting, and filtering options
    """
    bookings, count = await booking_repo.list_bookings(
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_direction=sort_direction,
        status_filter=status,
        date_from=date_from,
        date_to=date_to,
        service_id=service_id,
        customer_name=customer_name,
    )

    return PaginatedBookingRead(
        bookings=[BookingRead.model_validate(booking) for booking in bookings],
        total=count,  # Ensure this matches the field in PaginatedBookingRead
        page=skip // limit + 1 if limit > 0 else 1,  # Calculate page
        size=limit,  # Use limit as size
    )


@router.post(
    "/bookings", response_model=BookingRead, status_code=status.HTTP_201_CREATED
)
async def create_booking(
    booking_data: BookingCreate,
    booking_repo: BookingRepository = Depends(lambda: BookingRepository()),
) -> BookingRead:
    """
    Create a new booking
    """
    booking = await booking_repo.create_booking(booking_data.model_dump())
    return BookingRead.model_validate(booking)


@router.get("/bookings/{booking_id}", response_model=BookingRead)
async def get_booking(
    booking_id: str = Path(
        ..., description="The ID of the booking to retrieve"
    ),
    booking_repo: BookingRepository = Depends(lambda: BookingRepository()),
) -> BookingRead:
    """
    Get a booking by ID
    """
    booking = await booking_repo.get_booking(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found",
        )
    return BookingRead.model_validate(booking)


@router.put("/bookings/{booking_id}", response_model=BookingRead)
async def update_booking(
    booking_data: BookingUpdate,  # Moved to be before parameters with defaults
    booking_id: str = Path(..., description="The ID of the booking to update"),
    booking_repo: BookingRepository = Depends(lambda: BookingRepository()),
) -> BookingRead:
    """
    Update a booking by ID
    """
    updated_booking = await booking_repo.update_booking(
        booking_id, booking_data.model_dump(exclude_unset=True)
    )
    if not updated_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found for update",
        )
    return BookingRead.model_validate(updated_booking)


@router.patch("/bookings/{booking_id}/status", response_model=BookingRead)
async def patch_booking_status(
    status_data: BookingStatusUpdate,  # Moved to be before parameters with defaults
    booking_id: str = Path(
        ..., description="The ID of the booking to update status for"
    ),
    booking_repo: BookingRepository = Depends(lambda: BookingRepository()),
) -> BookingRead:
    """
    Update the status of a specific booking
    """
    updated_booking = await booking_repo.update_booking_status(
        booking_id, status_data.status
    )
    if not updated_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found for status update",
        )
    return BookingRead.model_validate(updated_booking)


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: str = Path(..., description="The ID of the booking to delete"),
    booking_repo: BookingRepository = Depends(lambda: BookingRepository()),
) -> None:
    """
    Delete a booking by ID
    """
    deleted = await booking_repo.delete_booking(booking_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found",
        )
    return None
