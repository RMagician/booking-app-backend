"""
Test service repository functions
"""

import pytest
from bson import ObjectId
from fastapi import HTTPException

from app.repositories.service_repository import ServiceRepository
from app.models.service import Service


@pytest.mark.asyncio
async def test_service_creation(test_db, service_repository: ServiceRepository):
    """Test creating a new service"""
    # Test data
    service_data = {
        "name": "Test Service",
        "description": "A test service",
        "duration": 60,
        "price": 100.00,
    }

    # Create service
    service = await service_repository.create_service(service_data)

    # Verify service was created with correct data
    assert service.name == "Test Service"
    assert service.description == "A test service"
    assert service.duration == 60
    assert service.price == 100.00
    assert service.id is not None

    # Verify service exists in the database
    retrieved_service = await service_repository.get_service(str(service.id))
    assert retrieved_service is not None
    assert retrieved_service.name == service.name


@pytest.mark.asyncio
async def test_service_get_nonexistent(
    test_db, service_repository: ServiceRepository
):
    """Test getting a nonexistent service"""
    # Generate a random ObjectId that doesn't exist in the database
    nonexistent_id = str(ObjectId())

    # Try to retrieve nonexistent service
    service = await service_repository.get_service(nonexistent_id)

    # Service should be None
    assert service is None


@pytest.mark.asyncio
async def test_service_invalid_id(service_repository: ServiceRepository):
    """Test error handling with invalid ID format"""
    # Use an invalid ID format
    invalid_id = "not-an-object-id"

    # Should raise HTTPException with 400 status
    with pytest.raises(HTTPException) as exc_info:
        await service_repository.get_service(invalid_id)

    # Verify exception details
    assert exc_info.value.status_code == 400
    assert "Invalid service ID format" in exc_info.value.detail
