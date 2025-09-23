import pytest
import uuid
from fastapi.testclient import TestClient

class TestAuthentication:
    
    def test_register_endpoint_exists(self, client):
        """Test that register endpoint exists."""
        response = client.post("/auth/register", json={})
        assert response.status_code != 404
    
    def test_register_with_valid_data(self, client, test_user_data):
        """Test user registration with valid data."""
        unique_email = f"test{uuid.uuid4().hex[:8]}@example.com"
        test_data = test_user_data.copy()
        test_data["email"] = unique_email
        
        response = client.post("/auth/register", json=test_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "user_id" in data
        assert "email" in data
        assert data["email"] == unique_email
    
    def test_register_with_invalid_email(self, client):
        """Test registration with invalid email format."""
        invalid_data = {
            "email": "invalid-email",
            "password": "password123",
            "preferred_name": "testuser"
        }
        
        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422
    
    def test_register_with_missing_fields(self, client):
        """Test registration with missing required fields."""
        incomplete_data = {
            "email": "test@example.com"
        }
        
        response = client.post("/auth/register", json=incomplete_data)
        assert response.status_code == 422
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email."""
        unique_email = f"duplicate{uuid.uuid4().hex[:8]}@example.com"
        test_data = {
            "email": unique_email,
            "password": "password123",
            "preferred_name": "user1"
        }
        response1 = client.post("/auth/register", json=test_data)
        assert response1.status_code == 200
        response2 = client.post("/auth/register", json=test_data)
        assert response2.status_code == 422

    def test_login_with_valid_credentials(self, client):
        """Test login with valid credentials returns JWT token."""
        # First register a user
        unique_email = f"login_test{uuid.uuid4().hex[:8]}@example.com"
        register_data = {
            "email": unique_email,
            "password": "password123",
            "preferred_name": "loginuser"
        }
        
        # Register
        register_response = client.post("/auth/register", json=register_data)
        assert register_response.status_code == 200
        
        # Now login
        login_data = {
            "email": unique_email,
            "password": "password123"
        }
        
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        data = login_response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user_id" in data
        assert data["email"] == unique_email

    def test_login_with_invalid_credentials(self, client):
        """Test login with invalid credentials fails."""
        invalid_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", json=invalid_data)
        assert response.status_code == 401
        
    def test_protected_route_with_valid_token(self, client):
        """Test accessing protected route with valid token."""
        # Register and login to get token
        unique_email = f"protected_test{uuid.uuid4().hex[:8]}@example.com"
        register_data = {
            "email": unique_email,
            "password": "password123", 
            "preferred_name": "protecteduser"
        }
        
        client.post("/auth/register", json=register_data)
        login_response = client.post("/auth/login", json={
            "email": unique_email,
            "password": "password123"
        })
        
        token = login_response.json()["access_token"]
        
        # Access protected route
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == unique_email
        assert "user_id" in data

    def test_protected_route_without_token(self, client):
        """Test accessing protected route without token fails."""
        response = client.get("/auth/me")
        assert response.status_code == 403  # Forbidden

class TestProfileCreation:
    
    def test_create_profile_success(self, client):
        """Test successful profile creation"""
        # Register and login first
        unique_email = f"profile_test{uuid.uuid4().hex[:8]}@example.com"
        register_data = {
            "email": unique_email,
            "password": "password123",
            "preferred_name": "profileuser"
        }
        
        client.post("/auth/register", json=register_data)
        login_response = client.post("/auth/login", json={
            "email": unique_email,
            "password": "password123"
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create profile
        profile_data = {
            "basic_info": {
                "name": "Test User",
                "title": "Software Engineer", 
                "email": unique_email,
                "summary": "Test summary"
            },
            "work_experience": [],
            "skills": {
                "programming_languages": ["Python"],
                "frameworks": ["FastAPI"],
                "databases": ["PostgreSQL"]
            },
            "projects": [],
            "education": []
        }
        
        response = client.post("/profile/create", json=profile_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "mcp_slug" in data
        assert "mcp_url" in data
        assert "profile_id" in data
    
    def test_create_profile_without_auth(self, client):
        """Test profile creation without authentication fails"""
        profile_data = {"basic_info": {"name": "Test"}}
        response = client.post("/profile/create", json=profile_data)
        assert response.status_code == 403

class TestMCPEndpoints:
    
    def test_mcp_tools_list(self, client):
        """Test MCP tools/list endpoint"""
        # Use the existing slug from your test
        response = client.post("/mcp/shoaib-lexca9e", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "tools" in data["result"]
        assert len(data["result"]["tools"]) == 3
    
    def test_mcp_nonexistent_user(self, client):
        """Test MCP endpoint with nonexistent user"""
        response = client.post("/mcp/nonexistent-user", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        })
        
        assert response.status_code == 404