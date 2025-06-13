"""
Booking repository module for database operations
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import HTTPException, status

from app.database import get_database
from app.models.booking import Booking, BookingStatus
from app.models.service import PyObjectId


class BookingRepository:
    """Repository for Booking model database operations"""

    collection_name = "bookings"

    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection for bookings"""
        db = get_database()
        return db[self.collection_name]

    async def ensure_indexes(self) -> None:
        """
        Ensure the necessary indexes exist in the database
        Should be called during application startup
        """
        # Create index on date field for efficient date queries
        await self.collection.create_index("date")

        # Create index on service_id for efficient service lookups
        await self.collection.create_index("service_id")

        # Create compound index on customer_name and date for searching customer bookings
        await self.collection.create_index([("customer_name", 1), ("date", 1)])

    async def create_booking(self, booking_data: Dict[str, Any]) -> Booking:
        """
        Create a new booking

        Args:
            booking_data: Booking data dictionary

        Returns:
            Booking: The created booking object
        """
        # Create a new booking object
        booking = Booking(**booking_data)

        # Insert the booking document into MongoDB
        result = await self.collection.insert_one(booking.to_mongo())

        # Update the ID with the generated ObjectID
        booking.id = result.inserted_id

        return booking

    async def get_booking(self, booking_id: str) -> Optional[Booking]:
        """
        Get a booking by ID

        Args:
            booking_id: The ID of the booking to retrieve

        Returns:
            Booking: The booking object or None if not found

        Raises:
            HTTPException: If the ID is not a valid ObjectId
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(booking_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid booking ID format: {booking_id}",
            )

        # Query the booking by ID
        document = await self.collection.find_one({"_id": object_id})
        return Booking.from_mongo(document)

    async def get_bookings_by_service(
        self, service_id: str, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Booking], int]:
        """
        Get bookings by service ID

        Args:
            service_id: The ID of the service
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            Tuple containing:
                - List of Booking objects
                - Total count of bookings for the service
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(service_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid service ID format: {service_id}",
            )

        # Get the total count
        total = await self.collection.count_documents(
            {"service_id": object_id}
        )  # Query with pagination
        cursor = self.collection.find({"service_id": object_id})
        cursor = cursor.sort("date", 1)  # Sort by date ascending
        cursor = cursor.skip(skip).limit(limit)

        # Convert MongoDB documents to Booking objects
        bookings = [Booking.from_mongo(document) async for document in cursor]

        return bookings, total

    async def list_bookings(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "date",
        sort_direction: int = 1,
        status_filter: Optional[BookingStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        service_id: Optional[str] = None,
        customer_name: Optional[str] = None,
    ) -> Tuple[List[Booking], int]:
        """
        List bookings with pagination, sorting and filtering

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            sort_by: Field to sort by
            sort_direction: Sort direction (1 for ascending, -1 for descending)
            status_filter: Filter by booking status (optional)
            date_from: Filter bookings from this date (inclusive, optional)
            date_to: Filter bookings until this date (inclusive, optional)
            service_id: Filter bookings by service ID (optional)
            customer_name: Search bookings by customer name (optional)

        Returns:
            Tuple containing:
                - List of Booking objects
                - Total count of bookings matching the criteria
        """
        # Prepare filter
        filter_query = {}

        if status_filter:
            filter_query["status"] = status_filter

        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = date_from
            if date_to:
                date_filter["$lte"] = date_to
            if date_filter:
                filter_query["date"] = date_filter

        # Filter by service_id if provided
        if service_id:
            try:
                service_object_id = ObjectId(service_id)
                filter_query["service_id"] = service_object_id
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid service ID format: {service_id}",
                )

        # Search by customer name (case-insensitive)
        if customer_name:
            filter_query["customer_name"] = {
                "$regex": customer_name,
                "$options": "i",
            }

        # Get the total count
        total = await self.collection.count_documents(filter_query)

        # Query with pagination and sorting
        cursor = self.collection.find(filter_query)
        cursor = cursor.sort(sort_by, sort_direction)
        cursor = cursor.skip(skip).limit(limit)

        # Convert MongoDB documents to Booking objects
        bookings = [Booking.from_mongo(document) async for document in cursor]

        return bookings, total

    async def update_booking(
        self, booking_id: str, update_data: Dict[str, Any]
    ) -> Optional[Booking]:
        """
        Update a booking by ID

        Args:
            booking_id: The ID of the booking to update
            update_data: Dictionary containing the fields to update

        Returns:
            Booking: The updated booking object or None if not found

        Raises:
            HTTPException: If the ID is not valid
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(booking_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid booking ID format: {booking_id}",
            )

        # Get the current booking data
        current_booking = await self.get_booking(booking_id)
        if not current_booking:
            return None

        # Prepare update data
        update_data["updated_at"] = datetime.utcnow()

        # Update the booking in MongoDB
        result = await self.collection.update_one(
            {"_id": object_id}, {"$set": update_data}
        )

        if result.modified_count == 0:
            # No document was modified
            return None

        # Retrieve and return the updated booking
        return await self.get_booking(booking_id)

    async def delete_booking(self, booking_id: str) -> bool:
        """
        Delete a booking by ID

        Args:
            booking_id: The ID of the booking to delete

        Returns:
            bool: True if the booking was deleted, False otherwise

        Raises:
            HTTPException: If the ID is not valid
        """
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(booking_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid booking ID format: {booking_id}",
            )

        # Delete the booking from MongoDB
        result = await self.collection.delete_one({"_id": object_id})

        # Return True if a document was deleted, False otherwise
        return result.deleted_count > 0
