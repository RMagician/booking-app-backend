"""
Service repository module for database operations
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import HTTPException, status

from app.database import get_database
from app.models.service import Service, PyObjectId


class ServiceRepository:
    """Repository for Service model database operations"""

    collection_name = "services"

    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection for services"""
        db = get_database()
        return db[self.collection_name]

    async def ensure_indexes(self) -> None:
        """
        Ensure the necessary indexes exist in the database
        Should be called during application startup
        """
        # Create a unique index on name to prevent duplicates
        await self.collection.create_index("name", unique=True)

        # Additional indexes can be added here as needed
        # Examples:
        # await self.collection.create_index([("price", 1)])  # Ascending index on price
        # await self.collection.create_index("duration")  # Index on duration

    async def create_service(self, service_data: Dict[str, Any]) -> Service:
        """
        Create a new service

        Args:
            service_data: Service data dictionary

        Returns:
            Service: The created service object

        Raises:
            HTTPException: If a service with the same name already exists
        """
        # Create a new service object
        service = Service(**service_data)

        try:
            # Insert the service document into MongoDB
            result = await self.collection.insert_one(service.to_mongo())

            # Update the ID with the generated ObjectID
            service.id = result.inserted_id

            return service
        except DuplicateKeyError:
            # Handle duplicate name
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Service with name '{service.name}' already exists",
            )

    async def get_service(self, service_id: str) -> Optional[Service]:
        """
        Get a service by ID

        Args:
            service_id: The ID of the service to retrieve

        Returns:
            Service: The service object or None if not found

        Raises:
            HTTPException: If the ID is not a valid ObjectId
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(service_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid service ID format: {service_id}",
            )

        # Query the service by ID
        document = await self.collection.find_one({"_id": object_id})
        return Service.from_mongo(document)

    async def get_service_by_name(self, name: str) -> Optional[Service]:
        """
        Get a service by name

        Args:
            name: The name of the service to retrieve

        Returns:
            Service: The service object or None if not found
        """
        # Query the service by name
        document = await self.collection.find_one({"name": name})
        return Service.from_mongo(document)

    async def list_services(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "name",
        sort_direction: int = 1,
    ) -> Tuple[List[Service], int]:
        """
        List services with pagination and sorting

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            sort_by: Field to sort by
            sort_direction: Sort direction (1 for ascending, -1 for descending)

        Returns:
            Tuple containing:
                - List of Service objects
                - Total count of services
        """
        # Get the total count
        total = await self.collection.count_documents({})

        # Query with pagination and sorting
        cursor = self.collection.find({})
        cursor = cursor.sort(sort_by, sort_direction)
        cursor = cursor.skip(skip).limit(limit)

        # Convert MongoDB documents to Service objects
        services = [Service.from_mongo(document) async for document in cursor]

        return services, total

    async def update_service(
        self, service_id: str, update_data: Dict[str, Any]
    ) -> Optional[Service]:
        """
        Update a service by ID

        Args:
            service_id: The ID of the service to update
            update_data: Dictionary containing the fields to update

        Returns:
            Service: The updated service object or None if not found

        Raises:
            HTTPException: If the ID is not valid or if there's a duplicate name
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(service_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid service ID format: {service_id}",
            )

        # Get the current service data
        current_service = await self.get_service(service_id)
        if not current_service:
            return None

        # Prepare update data
        update_data["updated_at"] = datetime.utcnow()

        try:
            # Update the service in MongoDB
            result = await self.collection.update_one(
                {"_id": object_id}, {"$set": update_data}
            )

            if result.modified_count == 0:
                # No document was modified
                return None

            # Retrieve and return the updated service
            return await self.get_service(service_id)
        except DuplicateKeyError:
            # Handle duplicate name
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Service with name '{update_data.get('name')}' already exists",
            )

    async def delete_service(self, service_id: str) -> bool:
        """
        Delete a service by ID

        Args:
            service_id: The ID of the service to delete

        Returns:
            bool: True if the service was deleted, False otherwise

        Raises:
            HTTPException: If the ID is not valid
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(service_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid service ID format: {service_id}",
            )

        # Delete the service from MongoDB
        result = await self.collection.delete_one({"_id": object_id})

        # Return True if a document was deleted, False otherwise
        return result.deleted_count > 0
