"""
Service model module
"""

from datetime import datetime, timezone  # Added timezone
from typing import Optional, Any, List
from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


# Custom PyObjectId class for Pydantic v2
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:

        def validate_from_str(value: str) -> ObjectId:
            """Converts a string to ObjectId, raises ValueError if invalid."""
            if ObjectId.is_valid(value):
                return ObjectId(value)
            raise ValueError(f"Invalid ObjectId string: {value}")

        object_id_schema = core_schema.is_instance_schema(ObjectId)

        # Schema for validating a string and converting to ObjectId
        str_to_object_id_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        # Union schema to allow either an ObjectId instance or a valid ObjectId string
        return core_schema.union_schema(
            [object_id_schema, str_to_object_id_schema],
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the Pydantic anystr_schema for JSON schema representation
        json_schema = handler(core_schema.str_schema())
        # Update with ObjectId specific details if needed, e.g., format or example
        json_schema.update(
            format="objectid",
            example="507f1f77bcf86cd799439011",  # Example ObjectId string
        )
        return json_schema


class Service(BaseModel):
    """
    Service model class representing a service offered in the booking system
    """

    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: Optional[str] = None
    price: float
    duration: int  # Duration in minutes
    availability: List[str] = []  # E.g., ["Monday 9-5", "Tuesday 10-4"]
    category: Optional[str] = None  # Added category
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = (
            True  # May still be needed if other non-Pydantic types are used
        )
        json_encoders = {
            ObjectId: str,
            PyObjectId: str,
        }  # Ensure PyObjectId is also encoded to str

    def __init__(self, **data: Any):
        raw_id = data.pop("id", None)
        raw_object_id = data.pop("_id", None)

        if raw_id is not None and isinstance(raw_id, str):
            data["id"] = PyObjectId(raw_id)
        elif raw_id is not None:  # Already PyObjectId or ObjectId
            data["id"] = raw_id
        elif raw_object_id is not None and isinstance(raw_object_id, str):
            data["id"] = PyObjectId(
                raw_object_id
            )  # Will be aliased to _id by Pydantic
        elif raw_object_id is not None:  # Already PyObjectId or ObjectId
            data["id"] = raw_object_id
        else:
            data["id"] = PyObjectId()  # Default factory if neither provided

        if "created_at" not in data or data["created_at"] is None:
            data["created_at"] = datetime.now(timezone.utc)
        if "updated_at" not in data or data["updated_at"] is None:
            data["updated_at"] = datetime.now(timezone.utc)

        super().__init__(**data)
        # Pydantic handles alias, self.id should be PyObjectId after super init
        # Ensure it is if it came from _id
        if raw_object_id is not None:
            if isinstance(self.id, ObjectId) and not isinstance(
                self.id, PyObjectId
            ):
                self.id = PyObjectId(self.id)  # Ensure it's PyObjectId instance
        elif self.id is None:  # Should be set by default_factory or above logic
            self.id = PyObjectId()

    def to_mongo(self) -> dict:
        data = self.model_dump(
            by_alias=True, exclude_none=True
        )  # by_alias=True will use '_id'

        if "_id" in data and isinstance(data["_id"], PyObjectId):
            data["_id"] = ObjectId(
                str(data["_id"])
            )  # Convert PyObjectId to ObjectId for DB
        elif "_id" in data and isinstance(data["_id"], str):
            data["_id"] = ObjectId(data["_id"])

        # Ensure datetimes are timezone-aware (UTC) and correctly formatted if strings
        for field_name in ["created_at", "updated_at"]:
            dt_value = getattr(self, field_name)
            if isinstance(dt_value, str):
                # Attempt to parse, assuming ISO format, make timezone-aware if naive
                parsed_dt = datetime.fromisoformat(
                    dt_value.replace("Z", "+00:00")
                )
                if parsed_dt.tzinfo is None:
                    parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
                data[field_name] = parsed_dt
            elif dt_value.tzinfo is None:  # Ensure timezone aware
                data[field_name] = dt_value.replace(tzinfo=timezone.utc)
            else:
                data[field_name] = dt_value

        return data

    @classmethod
    def from_mongo(cls, data: dict) -> "Service":
        if "_id" in data:
            data["id"] = data.pop("_id")
        return cls(**data)
