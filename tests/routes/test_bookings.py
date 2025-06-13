"""
Test booking endpoints
"""

import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi.testclient import TestClient

from app.models.booking import BookingStatus
from tests.utils.mock_data import create_mock_service_data


def test_create_booking(test_client: TestClient, test_db):
    """Test creating a booking through the API"""
    # First create a service to associate with the booking
    service_collection = test_db.get_collection("services")
    service_data = create_mock_service_data()
    service_collection.insert_one(service_data)
    service_id = str(service_data["_id"])

    # Booking data for the request
    booking_date = datetime.utcnow() + timedelta(days=1)
    booking_data = {
        "service_id": service_id,
        "customer_name": "API Test Customer",
        "date": booking_date.isoformat(),
        "status": BookingStatus.PENDING,
    }

    # Send request to create booking
    response = test_client.post("/api/bookings", json=booking_data)

    # Verify response
    assert response.status_code == 201

    # Verify data in response
    data = response.json()
    assert data["customer_name"] == "API Test Customer"
    assert data["status"] == "pending"
    assert "id" in data

    # Verify booking was saved to database
    booking_id = data["id"]
    booking_collection = test_db.get_collection("bookings")
    saved_booking = booking_collection.find_one({"_id": ObjectId(booking_id)})
    assert saved_booking is not None
    assert saved_booking["customer_name"] == "API Test Customer"


def test_get_booking(test_client: TestClient, test_db):
    """Test retrieving a booking through the API"""
    # Create a booking directly in the database
    booking_collection = test_db.get_collection("bookings")
    service_id = ObjectId()

    # Use current timestamps for created_at and updated_at
    now = datetime.utcnow()
    future_date = now + timedelta(days=2)

    booking_data = {
        "_id": ObjectId(),
        "service_id": service_id,
        "customer_name": "Get Test Customer",
        "date": future_date,
        "status": BookingStatus.CONFIRMED,
        "created_at": now,
        "updated_at": now,
    }

    booking_collection.insert_one(booking_data)
    booking_id = str(booking_data["_id"])

    # Retrieve the booking via API
    response = test_client.get(f"/api/bookings/{booking_id}")

    # Verify response
    assert response.status_code == 200

    # Verify data in response
    data = response.json()
    assert data["customer_name"] == "Get Test Customer"
    assert data["status"] == "confirmed"
    assert data["id"] == booking_id
