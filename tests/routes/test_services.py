"""
Test service endpoints
"""

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from tests.utils.mock_data import create_mock_service_data


def test_create_service(test_client: TestClient):
    """Test creating a service through the API"""
    # Prepare service data
    service_data = {
        "name": "API Test Service",
        "description": "A service created via API test",
        "duration": 45,
        "price": 75.00,
        "category": "api-testing",
    }

    # Send request to create service
    response = test_client.post("/api/services", json=service_data)

    # Verify response
    assert response.status_code == 201

    # Verify data in response
    data = response.json()
    assert data["name"] == "API Test Service"
    assert data["description"] == "A service created via API test"
    assert data["duration"] == 45
    assert data["price"] == 75.00
    assert data["category"] == "api-testing"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_services(test_client: TestClient, test_db):
    """Test listing services through the API"""
    # Create multiple services directly in the database
    service_collection = test_db.get_collection("services")

    # Clear any existing services
    await service_collection.delete_many({})

    # Create three test services
    service1 = create_mock_service_data()
    service1["name"] = "Test Service 1"
    service1["category"] = "category1"

    service2 = create_mock_service_data()
    service2["name"] = "Test Service 2"
    service2["category"] = "category1"

    service3 = create_mock_service_data()
    service3["name"] = "Test Service 3"
    service3["category"] = "category2"

    await service_collection.insert_many([service1, service2, service3])

    # Get services via API without filters
    response = test_client.get("/api/services")

    # Verify response
    assert response.status_code == 200

    # Verify data in response
    data = response.json()
    assert "services" in data  # Changed from "items"
    assert "count" in data  # Changed from "total"
    assert data["count"] == 3  # Changed from "total"
    assert len(data["services"]) == 3  # Changed from "items"

    # Test filtering by category
    response = test_client.get("/api/services?category=category1")

    # Verify filtered response
    data = response.json()
    assert "services" in data  # Changed from "items"
    assert "count" in data  # Changed from "total"
    assert data["count"] == 2  # Changed from "total"
    assert len(data["services"]) == 2  # Changed from "items"
    assert (
        data["services"][0]["category"] == "category1"
    )  # Changed from "items"
    assert (
        data["services"][1]["category"] == "category1"
    )  # Changed from "items"


@pytest.mark.asyncio
async def test_get_service(test_client: TestClient, test_db):
    """Test retrieving a single service through the API"""
    # Create a service directly in the database
    service_collection = test_db.get_collection("services")
    await service_collection.delete_many(
        {}
    )  # Good practice to clear before inserting for this test too
    service_data = create_mock_service_data()
    service_data["name"] = "Get Test Service"

    result = await service_collection.insert_one(service_data)  # Add await
    service_id = str(result.inserted_id)  # Use the id returned by insert_one

    # Retrieve the service via API
    response = test_client.get(f"/api/services/{service_id}")

    # Verify response
    assert response.status_code == 200

    # Verify data in response
    data = response.json()
    assert data["name"] == "Get Test Service"
    assert data["id"] == service_id
