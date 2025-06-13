"""
Service schema module for data validation and conversion
"""

from datetime import datetime
from typing import List, Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.service import PyObjectId


class ServiceBase(BaseModel):
    """Base schema for Service"""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Name of the service"
    )
    description: str = Field(
        "", max_length=1000, description="Description of the service"
    )
    duration: int = Field(
        ...,
        gt=0,
        le=480,  # Assuming max service duration is 8 hours (480 minutes)
        description="Duration of the service in minutes",
    )
    price: float = Field(..., ge=0, description="Price of the service")
    category: Optional[str] = Field(
        None, max_length=50, description="Category of the service"
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )

    # Validation for price - ensure it has at most 2 decimal places
    @field_validator("price")
    @classmethod
    def validate_price(cls, value: float) -> float:
        """Validate price to ensure it has at most 2 decimal places"""
        if value != round(value, 2):
            raise ValueError("Price must have at most 2 decimal places")
        return value

    # Validation for duration - ensure it's a multiple of 5 minutes
    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value: int) -> int:
        """Validate duration to ensure it's a multiple of 5 minutes"""
        if value % 5 != 0:
            raise ValueError("Duration must be a multiple of 5 minutes")
        return value


class ServiceCreate(ServiceBase):
    """Schema for creating a Service"""

    pass


class ServiceUpdate(BaseModel):
    """Schema for updating a Service - all fields optional"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    duration: Optional[int] = Field(None, gt=0, le=480)
    price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(
        None, max_length=50, description="Category of the service"
    )  # Added category

    # Validate price if provided
    @field_validator("price")
    @classmethod
    def validate_price(cls, value: Optional[float]) -> Optional[float]:
        """Validate price to ensure it has at most 2 decimal places"""
        if value is None:
            return value
        if value != round(value, 2):
            raise ValueError("Price must have at most 2 decimal places")
        return value

    # Validate duration if provided
    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value: Optional[int]) -> Optional[int]:
        """Validate duration to ensure it's a multiple of 5 minutes"""
        if value is None:
            return value
        if value % 5 != 0:
            raise ValueError("Duration must be a multiple of 5 minutes")
        return value

    # Ensure at least one field is set
    @field_validator(
        "name", "description", "duration", "price", "category"
    )  # Added category to validator
    @classmethod
    def check_at_least_one_field(cls, value, info):
        """Ensure at least one field is provided for update"""
        values = info.data
        if all(v is None for v in values.values()):
            raise ValueError("At least one field must be provided for update")
        return value

    model_config = ConfigDict(extra="forbid")  # Prevent additional fields


class ServiceRead(ServiceBase):
    """Schema for reading a Service"""

    id: PyObjectId = Field(..., description="Unique identifier for the service")
    created_at: datetime
    updated_at: datetime
    # category is inherited from ServiceBase and will be Optional[str]
    # If category should always be present in ServiceRead, define it here explicitly as str, e.g.:
    # category: Optional[str] = Field(None, max_length=50, description="Category of the service")
    # For now, it will be Optional as per ServiceBase.

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={
            PyObjectId: str
        },  # Ensure PyObjectId is serialized to string
    )


class PaginatedServiceRead(BaseModel):
    """Schema for paginated listing of Services"""

    services: List[ServiceRead]
    count: int  # Total number of services matching the query
    page: int
    size: int

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={PyObjectId: str},
    )
