"""
Test health endpoints
"""

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(test_client: TestClient):
    """Test health endpoint returns the correct status"""
    response = test_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
