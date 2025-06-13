"""
Service model module
"""

from datetime import datetime
from typing import Optional
from bson import ObjectId


class PyObjectId(ObjectId):
    """
    Custom ObjectId class that implements the required interface for Pydantic models
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Service:
    """
    Service model class representing a service offered in the booking system
    """

    def __init__(
        self,
        id: Optional[PyObjectId] = None,
        name: str = "",
        description: str = "",
        duration: int = 0,  # in minutes
        price: float = 0.0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs,
    ):
        """
        Initialize a Service object

        Args:
            id: The ObjectId of the service
            name: The name of the service
            description: The description of the service
            duration: The duration of the service in minutes
            price: The price of the service
            created_at: The creation timestamp
            updated_at: The last update timestamp
        """
        self.id = id or PyObjectId()
        self.name = name
        self.description = description
        self.duration = duration
        self.price = price
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or self.created_at

    @classmethod
    def from_mongo(cls, data: dict):
        """
        Create a Service object from MongoDB document

        Args:
            data: The MongoDB document

        Returns:
            Service: A Service object
        """
        if not data:
            return None

        # Convert MongoDB _id to id
        if data.get("_id"):
            data["id"] = data.pop("_id")

        return cls(**data)

    def to_mongo(self) -> dict:
        """
        Convert this Service object to a MongoDB document

        Returns:
            dict: A MongoDB document
        """
        # Create a copy of self.__dict__
        document = self.__dict__.copy()

        # Convert id to _id for MongoDB
        document["_id"] = document.pop("id")

        return document
