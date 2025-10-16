import pytest
import asyncio
import time
from fastapi.testclient import TestClient
from app import app
from app.core.database import get_supabase_client
from tests.test_utils import rate_limited_register

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

@pytest.fixture
def metrics_collector():
    """Get the metrics collector instance."""
    from app.core.observability import get_metrics_collector
    return get_metrics_collector()

@pytest.fixture
def clear_metrics():
    """Clear all metrics before and after test."""
    from app.core.observability import get_metrics_collector
    collector = get_metrics_collector()
    collector.clear_old_metrics(hours=0)
    yield
    # Optionally clear after test as well
    # collector.clear_old_metrics(hours=0)

@pytest.fixture
def auth_token(client):
    """Create a test user and return valid auth token."""
    import uuid
    unique_email = f"auth_fixture{uuid.uuid4().hex[:8]}@example.com"
    register_data = {
        "email": unique_email,
        "password": "password123",
        "preferred_name": "authuser"
    }

    # Use rate-limited registration
    register_response = rate_limited_register(client, register_data)
    assert register_response.status_code == 200, f"Registration failed: {register_response.json()}"

    # Small delay to allow registration to complete
    time.sleep(0.3)

    login_response = client.post("/auth/login", json={
        "email": unique_email,
        "password": "password123"
    })
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"

    login_data = login_response.json()
    assert "access_token" in login_data, f"No access_token in response: {login_data}"
    return login_data["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    """Return authorization headers with valid token."""
    return {"Authorization": f"Bearer {auth_token}"}