"""
Booking schema module for data validation and conversion
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.models.booking import BookingStatus


class BookingBase(BaseModel):
    """Base schema for Booking"""

    customer_name: str = Field(
        ..., min_length=2, max_length=100, description="Name of the customer"
    )
    date: datetime = Field(..., description="Date and time of the booking")
    service_id: str = Field(..., description="ID of the service being booked")
    status: BookingStatus = Field(
        default=BookingStatus.PENDING, description="Status of the booking"
    )

    # Validate booking date - no past bookings
    @field_validator("date")
    @classmethod
    def validate_booking_date(cls, value: datetime) -> datetime:
        """Validate booking date to ensure it's not in the past"""
        now = datetime.utcnow()
        if value < now:
            raise ValueError("Booking date cannot be in the past")
        return value


class BookingCreate(BookingBase):
    """Schema for creating a Booking"""

    # For creating a booking, status can only be pending or confirmed
    @field_validator("status")
    @classmethod
    def validate_status_on_create(cls, value: BookingStatus) -> BookingStatus:
        """Validate that status can only be pending or confirmed on create"""
        if value not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise ValueError(
                f"Status on booking creation can only be {BookingStatus.PENDING} or {BookingStatus.CONFIRMED}"
            )
        return value


class BookingStatusUpdate(BaseModel):
    """Schema for updating just the status of a Booking"""

    status: BookingStatus = Field(..., description="New status of the booking")


class BookingUpdate(BaseModel):
    """Schema for updating a Booking - all fields optional"""

    customer_name: Optional[str] = Field(None, min_length=2, max_length=100)
    date: Optional[datetime] = None
    service_id: Optional[str] = None
    status: Optional[BookingStatus] = None

    # Validate booking date if provided
    @field_validator("date")
    @classmethod
    def validate_booking_date(
        cls, value: Optional[datetime]
    ) -> Optional[datetime]:
        """Validate booking date to ensure it's not in the past"""
        if value is None:
            return value
        now = datetime.utcnow()
        if value < now:
            raise ValueError("Booking date cannot be in the past")
        return value

    # Ensure at least one field is set
    @field_validator("customer_name", "date", "service_id", "status")
    @classmethod
    def check_at_least_one_field(cls, value, info):
        """Ensure at least one field is provided for update"""
        values = info.data
        if all(v is None for v in values.values()):
            raise ValueError("At least one field must be provided for update")
        return value

    model_config = ConfigDict(extra="forbid")  # Prevent additional fields


class BookingRead(BookingBase):
    """Schema for reading a Booking"""

    id: str = Field(..., description="Unique identifier for the booking")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "6150d1a73f6c06dd3d9e2d1c",
                "customer_name": "John Doe",
                "date": "2023-10-15T14:30:00",
                "service_id": "6150d1a73f6c06dd3d9e2d1b",
                "status": "pending",
                "created_at": "2023-09-26T10:00:00",
                "updated_at": "2023-09-26T10:00:00",
            }
        },
    )


class BookingList(BaseModel):
    """Schema for listing Bookings"""

    bookings: List[BookingRead]
    count: int
