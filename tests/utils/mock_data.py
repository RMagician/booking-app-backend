"""
Mock data and helper functions for testing
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from bson import ObjectId

from app.models.booking import BookingStatus


def create_mock_service_data() -> Dict[str, Any]:
    """Create mock service data for tests"""
    return {
        "_id": ObjectId(),
        "name": "Mock Service",
        "description": "A mock service for testing",
        "duration": 60,
        "price": 100.00,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def create_mock_booking_data(service_id: ObjectId = None) -> Dict[str, Any]:
    """Create mock booking data for tests"""
    if not service_id:
        service_id = ObjectId()

    return {
        "_id": ObjectId(),
        "service_id": service_id,
        "customer_name": "Mock Customer",
        "date": datetime.utcnow() + timedelta(days=1),
        "status": BookingStatus.PENDING,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
