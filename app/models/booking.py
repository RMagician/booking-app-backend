"""
Booking model module
"""

from datetime import datetime
from enum import Enum, auto
from typing import Optional

from app.models.service import PyObjectId


class BookingStatus(str, Enum):
    """Enum for booking status"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    COMPLETED = "completed"


class Booking:
    """
    Booking model class representing a customer booking in the system
    """

    def __init__(
        self,
        id: Optional[PyObjectId] = None,
        customer_name: str = "",
        date: datetime = None,
        service_id: PyObjectId = None,
        status: str = BookingStatus.PENDING,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs,
    ):
        """
        Initialize a Booking object

        Args:
            id: The ObjectId of the booking
            customer_name: The name of the customer
            date: The date and time of the booking
            service_id: The ID of the service being booked
            status: The status of the booking
            created_at: The creation timestamp
            updated_at: The last update timestamp
        """
        self.id = id or PyObjectId()
        self.customer_name = customer_name
        self.date = date or datetime.utcnow()
        self.service_id = service_id
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or self.created_at

    @classmethod
    def from_mongo(cls, data: dict):
        """
        Create a Booking object from MongoDB document

        Args:
            data: The MongoDB document

        Returns:
            Booking: A Booking object
        """
        if not data:
            return None

        # Convert MongoDB _id to id
        if data.get("_id"):
            data["id"] = data.pop("_id")

        # Convert service_id to PyObjectId if it exists
        if data.get("service_id") and isinstance(data["service_id"], dict):
            data["service_id"] = PyObjectId(data["service_id"])

        return cls(**data)

    def to_mongo(self) -> dict:
        """
        Convert this Booking object to a MongoDB document

        Returns:
            dict: A MongoDB document
        """
        # Create a copy of self.__dict__
        document = self.__dict__.copy()

        # Convert id to _id for MongoDB
        document["_id"] = document.pop("id")

        return document
