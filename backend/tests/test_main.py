import pytest
from fastapi.testclient import TestClient

class TestMainEndpoints:
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert data["service"] == "Vocalaa API"
    
    def test_root_endpoint_not_found(self, client):
        """Test that root endpoint returns 404 (as expected)."""
        response = client.get("/")
        assert response.status_code == 404
    
    def test_nonexistent_endpoint(self, client):
        """Test that nonexistent endpoints return 404."""
        response = client.get("/nonexistent")
        assert response.status_code == 404