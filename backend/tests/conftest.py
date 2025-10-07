import pytest
import asyncio
from fastapi.testclient import TestClient
from app import app
from app.core.database import get_supabase_client

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create a test client for FastAPI."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def supabase_client():
    """Get Supabase client for testing."""
    return get_supabase_client()

@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "preferred_name": "testuser"
    }