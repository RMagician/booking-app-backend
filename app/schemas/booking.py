"""
Booking schema module for data validation and conversion
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.booking import BookingStatus
from app.models.service import PyObjectId  # Import the new PyObjectId


class BookingBase(BaseModel):
    """Base schema for Booking"""

    customer_name: str = Field(
        ..., min_length=2, max_length=100, description="Name of the customer"
    )
    date: datetime = Field(..., description="Date and time of the booking")
    service_id: PyObjectId = Field(
        ..., description="ID of the service being booked"
    )
    status: BookingStatus = Field(
        default=BookingStatus.PENDING, description="Status of the booking"
    )

    model_config = ConfigDict(
        populate_by_name=True,
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
    service_id: Optional[PyObjectId] = None
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

    model_config = ConfigDict(extra="forbid")  # Ensured this line


class BookingRead(BookingBase):
    """Schema for reading a Booking"""

    id: PyObjectId = Field(..., description="Unique identifier for the booking")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={
            PyObjectId: str
        },  # Ensure PyObjectId is serialized to string
    )


class PaginatedBookingRead(BaseModel):
    """Schema for paginated booking results"""

    bookings: List[BookingRead]
    total: int  # Assuming this means total bookings matching query
    page: int
    size: int

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={PyObjectId: str},
    )
