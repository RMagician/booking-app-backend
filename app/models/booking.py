"""
Booking model module
"""

from datetime import datetime, timezone  # Added timezone
from enum import Enum
from typing import Optional, Any
from bson import ObjectId
from pydantic import BaseModel, Field
from app.models.service import PyObjectId  # Import the new PyObjectId


class BookingStatus(str, Enum):
    """Enum for booking status"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    COMPLETED = "completed"


class Booking(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    service_id: PyObjectId
    booking_time: datetime
    status: str = "confirmed"
    notes: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, PyObjectId: str}

    def __init__(self, **data: Any):
        raw_id = data.pop("id", None)
        raw_object_id = data.pop("_id", None)

        if raw_id is not None and isinstance(raw_id, str):
            data["id"] = PyObjectId(raw_id)
        elif raw_id is not None:
            data["id"] = raw_id
        elif raw_object_id is not None and isinstance(raw_object_id, str):
            data["id"] = PyObjectId(raw_object_id)
        elif raw_object_id is not None:
            data["id"] = raw_object_id
        else:
            data["id"] = PyObjectId()

        if "service_id" in data and isinstance(data["service_id"], str):
            data["service_id"] = PyObjectId(data["service_id"])
        elif (
            "service_id" in data
            and isinstance(data["service_id"], ObjectId)
            and not isinstance(data["service_id"], PyObjectId)
        ):
            data["service_id"] = PyObjectId(data["service_id"])

        if "created_at" not in data or data["created_at"] is None:
            data["created_at"] = datetime.now(timezone.utc)
        if "updated_at" not in data or data["updated_at"] is None:
            data["updated_at"] = datetime.now(timezone.utc)

        super().__init__(**data)
        if raw_object_id is not None:
            if isinstance(self.id, ObjectId) and not isinstance(
                self.id, PyObjectId
            ):
                self.id = PyObjectId(self.id)
        elif self.id is None:
            self.id = PyObjectId()

        if isinstance(self.service_id, ObjectId) and not isinstance(
            self.service_id, PyObjectId
        ):
            self.service_id = PyObjectId(self.service_id)

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        # Ensure _id is an ObjectId
        if "_id" in data and isinstance(data["_id"], PyObjectId):
            data["_id"] = ObjectId(str(data["_id"]))
        # Robustly convert service_id to ObjectId if needed
        if "service_id" in data:
            if isinstance(data["service_id"], PyObjectId):
                data["service_id"] = ObjectId(str(data["service_id"]))
            elif isinstance(data["service_id"], str):
                # If it's a valid ObjectId string, convert it
                try:
                    data["service_id"] = ObjectId(data["service_id"])
                except Exception:
                    pass  # Leave as is if not a valid ObjectId string
        # Ensure datetimes are timezone-aware and in correct format
        for field_name in ["created_at", "updated_at", "booking_time"]:
            dt_value = getattr(self, field_name)
            if isinstance(dt_value, str):
                parsed_dt = datetime.fromisoformat(
                    dt_value.replace("Z", "+00:00")
                )
                if parsed_dt.tzinfo is None:
                    parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
                data[field_name] = parsed_dt
            elif dt_value.tzinfo is None:
                data[field_name] = dt_value.replace(tzinfo=timezone.utc)
            else:
                data[field_name] = dt_value
        return data

    @classmethod
    def from_mongo(cls, data: dict) -> "Booking":
        if "_id" in data:
            data["id"] = data.pop("_id")
        if "service_id" in data and isinstance(data["service_id"], ObjectId):
            # Pydantic will convert to PyObjectId via validation if the field type is PyObjectId
            pass
        return cls(**data)
