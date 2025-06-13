"""
Test booking repository functions
"""

import pytest
from datetime import datetime, timedelta, timezone  # Added timezone
from bson import ObjectId

from app.repositories.booking_repository import BookingRepository
from app.models.booking import Booking, BookingStatus


@pytest.mark.asyncio
async def test_booking_creation(test_db, booking_repository: BookingRepository):
    """Test creating a new booking"""
    # Test data
    service_id = ObjectId()
    booking_data = {
        "user_id": "test_user_123",  # Added user_id
        "service_id": service_id,
        "customer_name": "Test Customer",
        "booking_time": datetime.now(timezone.utc)
        + timedelta(days=1),  # Renamed date to booking_time and updated utcnow
        "status": BookingStatus.PENDING,
    }

    # Create booking
    booking: Booking = await booking_repository.create_booking(booking_data)

    # Verify booking was created with correct data
    assert booking.status == BookingStatus.PENDING
    assert booking.id is not None
    assert booking.user_id == "test_user_123"

    # Verify booking exists in the database
    retrieved_booking = await booking_repository.get_booking(str(booking.id))
    assert retrieved_booking is not None
    assert retrieved_booking.user_id == booking.user_id


@pytest.mark.asyncio
async def test_get_bookings_by_service(
    test_db, booking_repository: BookingRepository
):
    """Test retrieving bookings by service ID"""
    # Create a service ID
    service_id = ObjectId()

    # Create multiple bookings for the service
    booking_data_1 = {
        "user_id": "user_service_test_1",  # Added user_id
        "service_id": service_id,
        "customer_name": "Customer 1",
        "booking_time": datetime.now(timezone.utc)
        + timedelta(days=1),  # Renamed date to booking_time and updated utcnow
        "status": BookingStatus.PENDING,
    }

    booking_data_2 = {
        "user_id": "user_service_test_2",  # Added user_id
        "service_id": service_id,
        "customer_name": "Customer 2",
        "booking_time": datetime.now(timezone.utc)
        + timedelta(days=2),  # Renamed date to booking_time and updated utcnow
        "status": BookingStatus.CONFIRMED,
    }

    # Create the bookings
    booking1 = await booking_repository.create_booking(booking_data_1)
    booking2: Booking = await booking_repository.create_booking(booking_data_2)

    # Get bookings for the service
    bookings, count = await booking_repository.get_bookings_by_service(
        str(service_id)
    )

    # Verify results
    assert count == 2
    assert len(bookings) == 2
    # Order might not be guaranteed, so check for presence or sort before asserting specific indices
    customer_names_retrieved = sorted([b.user_id for b in bookings])
    expected_customer_names = sorted([booking1.user_id, booking2.user_id])
    assert customer_names_retrieved == expected_customer_names


@pytest.mark.asyncio
async def test_update_booking(test_db, booking_repository: BookingRepository):
    """Test updating a booking"""
    # Create a booking
    booking_data = {
        "user_id": "user_update_test",  # Added user_id
        "service_id": ObjectId(),
        "customer_name": "Original Name",
        "booking_time": datetime.now(timezone.utc)
        + timedelta(days=1),  # Renamed date to booking_time and updated utcnow
        "status": BookingStatus.PENDING,
    }

    booking = await booking_repository.create_booking(booking_data)

    # Update data
    update_data = {
        "user_id": "Updated Name",
        "status": BookingStatus.CONFIRMED,
    }

    # Update booking
    updated_booking = await booking_repository.update_booking(
        str(booking.id), update_data
    )

    # Verify update
    assert updated_booking.user_id == "Updated Name"
    assert updated_booking.status == BookingStatus.CONFIRMED

    # Verify in database
    db_booking = await booking_repository.get_booking(str(booking.id))
    assert db_booking.user_id == "Updated Name"
    assert db_booking.status == BookingStatus.CONFIRMED
