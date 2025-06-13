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
    BookingList,
    BookingStatusUpdate,
)
from app.models.booking import BookingStatus

# Define the router with the "bookings" tag
router = APIRouter(tags=["bookings"])


@router.get("/bookings", response_model=BookingList)
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
    booking_repo: BookingRepository = Depends(lambda: BookingRepository()),
) -> BookingList:
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
    )

    return BookingList(
        bookings=[
            BookingRead.model_validate(booking.__dict__) for booking in bookings
        ],
        count=count,
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
    return BookingRead.model_validate(booking.__dict__)


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
    return BookingRead.model_validate(booking.__dict__)


@router.put("/bookings/{booking_id}/status", response_model=BookingRead)
async def update_booking_status(
    status_data: BookingStatusUpdate,
    booking_id: str = Path(
        ..., description="The ID of the booking to update status"
    ),
    booking_repo: BookingRepository = Depends(lambda: BookingRepository()),
) -> BookingRead:
    """
    Update a booking's status (Confirmed, Pending, Canceled)
    """
    updated_booking = await booking_repo.update_booking(
        booking_id, {"status": status_data.status}
    )
    if not updated_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found",
        )
    return BookingRead.model_validate(updated_booking.__dict__)


@router.get("/services/{service_id}/bookings", response_model=BookingList)
async def list_service_bookings(
    service_id: str = Path(..., description="The ID of the service"),
    skip: int = Query(0, ge=0, description="Number of bookings to skip"),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of bookings to return"
    ),
    booking_repo: BookingRepository = Depends(lambda: BookingRepository()),
) -> BookingList:
    """
    List all bookings for a specific service
    """
    bookings, count = await booking_repo.get_bookings_by_service(
        service_id=service_id, skip=skip, limit=limit
    )

    return BookingList(
        bookings=[
            BookingRead.model_validate(booking.__dict__) for booking in bookings
        ],
        count=count,
    )


@router.put("/bookings/{booking_id}", response_model=BookingRead)
async def update_booking(
    booking_data: BookingUpdate,
    booking_id: str = Path(..., description="The ID of the booking to update"),
    booking_repo: BookingRepository = Depends(lambda: BookingRepository()),
) -> BookingRead:
    """
    Update a booking by ID
    """
    # Filter out None values to prevent overwriting with None
    update_data = {
        k: v for k, v in booking_data.model_dump().items() if v is not None
    }

    updated_booking = await booking_repo.update_booking(booking_id, update_data)
    if not updated_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found",
        )
    return BookingRead.model_validate(updated_booking.__dict__)


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
