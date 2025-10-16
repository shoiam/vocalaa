import pytest
import uuid
import time
from fastapi.testclient import TestClient
from app.core.observability import get_metrics_collector
from datetime import datetime
from tests.test_utils import rate_limited_register


class TestMCPObservability:
    """Test that MCP operations are properly tracked by observability"""

    @pytest.fixture
    def test_user_profile(self, client):
        """Create a test user with profile for MCP testing"""
        # Register user
        unique_email = f"mcp_obs_test{uuid.uuid4().hex[:8]}@example.com"
        register_data = {
            "email": unique_email,
            "password": "password123",
            "preferred_name": "mcpobsuser"
        }

        register_response = rate_limited_register(client, register_data)
        assert register_response.status_code == 200, f"Registration failed: {register_response.json()}"

        # Small delay to allow registration to complete
        time.sleep(0.3)

        # Login to get token
        login_response = client.post("/auth/login", json={
            "email": unique_email,
            "password": "password123"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.json()}"

        login_data = login_response.json()
        assert "access_token" in login_data, f"No access_token in response: {login_data}"
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create profile
        profile_data = {
            "basic_info": {
                "name": "Test User",
                "title": "Software Engineer",
                "email": unique_email,
                "location": "Test City",
                "summary": "Test summary"
            },
            "work_experience": [
                {
                    "role": "Engineer",
                    "company": "Test Corp",
                    "duration": "2020-2023",
                    "description": "Test work",
                    "achievements": ["Achievement 1"]
                }
            ],
            "skills": {
                "programming_languages": ["Python", "JavaScript"],
                "frameworks": ["FastAPI", "React"],
                "databases": ["PostgreSQL"]
            },
            "projects": [
                {
                    "name": "Test Project",
                    "description": "A test project",
                    "technologies": ["Python"],
                    "github_url": "https://github.com/test/project"
                }
            ],
            "education": [
                {
                    "degree": "BS",
                    "field": "Computer Science",
                    "institution": "Test University",
                    "graduation_year": "2020"
                }
            ]
        }

        profile_response = client.post("/profile/create", json=profile_data, headers=headers)
        assert profile_response.status_code == 200, f"Profile creation failed: {profile_response.json()}"

        profile_data_response = profile_response.json()
        assert "mcp_slug" in profile_data_response, f"No mcp_slug in response: {profile_data_response}"
        mcp_slug = profile_data_response["mcp_slug"]

        return {
            "mcp_slug": mcp_slug,
            "email": unique_email,
            "token": token
        }

    def test_tool_call_metrics_recorded(self, client, test_user_profile):
        """Test that tool calls are recorded in metrics"""
        collector = get_metrics_collector()
        initial_count = len(collector._tool_metrics)

        # Make MCP tool call
        response = client.post(f"/mcp/{test_user_profile['mcp_slug']}", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "get_basic_info"}
        })

        assert response.status_code == 200

        # Check that metrics were recorded
        assert len(collector._tool_metrics) > initial_count

        # Find our metric
        latest_metrics = [m for m in collector._tool_metrics if m.user_slug == test_user_profile['mcp_slug']]
        assert len(latest_metrics) > 0

        latest_metric = latest_metrics[-1]
        assert latest_metric.tool_name == "get_basic_info"
        assert latest_metric.success is True
        assert latest_metric.duration_ms > 0

    def test_multiple_tool_calls_tracked(self, client, test_user_profile):
        """Test that multiple tool calls are tracked separately"""
        collector = get_metrics_collector()

        tools = ["get_basic_info", "get_work_experience", "get_skills"]

        for tool in tools:
            response = client.post(f"/mcp/{test_user_profile['mcp_slug']}", json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": tool}
            })
            assert response.status_code == 200

        # Get metrics for this user
        user_metrics = [m for m in collector._tool_metrics if m.user_slug == test_user_profile['mcp_slug']]

        # Should have metrics for all three tools
        recorded_tools = set(m.tool_name for m in user_metrics)
        assert "get_basic_info" in recorded_tools
        assert "get_work_experience" in recorded_tools
        assert "get_skills" in recorded_tools

    def test_failed_tool_call_tracked(self, client, test_user_profile):
        """Test that failed tool calls are tracked with error info"""
        collector = get_metrics_collector()
        initial_errors = sum(1 for m in collector._tool_metrics if not m.success)

        # Call non-existent tool
        response = client.post(f"/mcp/{test_user_profile['mcp_slug']}", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "nonexistent_tool"}
        })

        # MCP should return error response
        data = response.json()
        assert "error" in data

        # Check that error was tracked
        current_errors = sum(1 for m in collector._tool_metrics if not m.success)
        assert current_errors > initial_errors

        # Find the error metric
        error_metrics = [m for m in collector._tool_metrics
                        if m.user_slug == test_user_profile['mcp_slug'] and not m.success]

        if error_metrics:
            latest_error = error_metrics[-1]
            assert latest_error.tool_name == "nonexistent_tool"
            assert latest_error.error_message is not None

    def test_tool_call_duration_tracked(self, client, test_user_profile):
        """Test that tool call duration is tracked"""
        collector = get_metrics_collector()

        response = client.post(f"/mcp/{test_user_profile['mcp_slug']}", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "get_basic_info"}
        })

        assert response.status_code == 200

        # Get the latest metric for this user
        user_metrics = [m for m in collector._tool_metrics if m.user_slug == test_user_profile['mcp_slug']]
        latest_metric = user_metrics[-1]

        # Duration should be recorded and > 0
        assert latest_metric.duration_ms > 0
        assert isinstance(latest_metric.duration_ms, float)

    def test_request_id_tracked(self, client, test_user_profile):
        """Test that request IDs are tracked"""
        collector = get_metrics_collector()
        request_id = 12345

        response = client.post(f"/mcp/{test_user_profile['mcp_slug']}", json={
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {"name": "get_basic_info"}
        })

        assert response.status_code == 200

        # Find metric with this request ID
        matching_metrics = [m for m in collector._tool_metrics if m.request_id == request_id]
        assert len(matching_metrics) > 0

    def test_timestamp_recorded(self, client, test_user_profile):
        """Test that timestamps are recorded correctly"""
        collector = get_metrics_collector()
        before_call = datetime.utcnow()

        response = client.post(f"/mcp/{test_user_profile['mcp_slug']}", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "get_basic_info"}
        })

        after_call = datetime.utcnow()
        assert response.status_code == 200

        # Get the latest metric
        user_metrics = [m for m in collector._tool_metrics if m.user_slug == test_user_profile['mcp_slug']]
        latest_metric = user_metrics[-1]

        # Parse timestamp
        metric_time = datetime.fromisoformat(latest_metric.timestamp)

        # Timestamp should be between before and after
        assert before_call <= metric_time <= after_call

    def test_metrics_available_in_api(self, client, test_user_profile):
        """Test that MCP tool calls show up in metrics API"""
        # First, get auth token for metrics API
        unique_email = f"metrics_api_test{uuid.uuid4().hex[:8]}@example.com"
        register_data = {
            "email": unique_email,
            "password": "password123",
            "preferred_name": "metricsapiuser"
        }

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
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Make several MCP tool calls
        for _ in range(3):
            client.post(f"/mcp/{test_user_profile['mcp_slug']}", json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "get_basic_info"}
            })

        # Get metrics from API
        response = client.get("/metrics/tools", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["total_calls"] >= 3

    def test_user_activity_tracking(self, client, test_user_profile):
        """Test that user activity is tracked correctly"""
        # Create another user for auth
        unique_email = f"activity_test{uuid.uuid4().hex[:8]}@example.com"
        register_data = {
            "email": unique_email,
            "password": "password123",
            "preferred_name": "activityuser"
        }

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
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Make tool calls
        tools = ["get_basic_info", "get_skills"]
        for tool in tools:
            client.post(f"/mcp/{test_user_profile['mcp_slug']}", json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": tool}
            })

        # Check user activity metrics
        response = client.get("/metrics/users", headers=headers)
        assert response.status_code == 200

        data = response.json()

        # Should have activity for our test user
        if test_user_profile['mcp_slug'] in data["users"]:
            user_stats = data["users"][test_user_profile['mcp_slug']]
            assert user_stats["total_calls"] >= 2
            assert user_stats["unique_tools"] >= 2


class TestMCPInitializeMetrics:
    """Test metrics for MCP initialize method"""

    @pytest.fixture
    def test_user_slug(self, client):
        """Create a test user and return MCP slug"""
        unique_email = f"init_test{uuid.uuid4().hex[:8]}@example.com"
        register_data = {
            "email": unique_email,
            "password": "password123",
            "preferred_name": "inituser"
        }

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
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        profile_data = {
            "basic_info": {
                "name": "Init Test",
                "title": "Engineer",
                "email": unique_email,
                "summary": "Test"
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

        profile_response = client.post("/profile/create", json=profile_data, headers=headers)
        assert profile_response.status_code == 200, f"Profile creation failed: {profile_response.json()}"

        profile_data_response = profile_response.json()
        assert "mcp_slug" in profile_data_response, f"No mcp_slug in response: {profile_data_response}"
        return profile_data_response["mcp_slug"]

    def test_initialize_call_succeeds(self, client, test_user_slug):
        """Test that MCP initialize call succeeds"""
        response = client.post(f"/mcp/{test_user_slug}", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        })

        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert data["result"]["serverInfo"]["name"] == f"vocalaa-{test_user_slug}"

    def test_tools_list_call_succeeds(self, client, test_user_slug):
        """Test that MCP tools/list call succeeds"""
        response = client.post(f"/mcp/{test_user_slug}", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        })

        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "tools" in data["result"]
        assert len(data["result"]["tools"]) == 5  # Based on your mcp_service.py


class TestMCPMetricsIntegration:
    """Test end-to-end integration of MCP with metrics"""

    def test_complete_workflow_tracking(self, client):
        """Test complete workflow from user creation to metrics retrieval"""
        # 1. Create user
        unique_email = f"workflow_test{uuid.uuid4().hex[:8]}@example.com"
        register_data = {
            "email": unique_email,
            "password": "password123",
            "preferred_name": "workflowuser"
        }

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
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create profile
        profile_data = {
            "basic_info": {
                "name": "Workflow Test",
                "title": "Developer",
                "email": unique_email,
                "summary": "Test user"
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

        profile_response = client.post("/profile/create", json=profile_data, headers=headers)
        assert profile_response.status_code == 200, f"Profile creation failed: {profile_response.json()}"

        profile_data_response = profile_response.json()
        assert "mcp_slug" in profile_data_response, f"No mcp_slug in response: {profile_data_response}"
        mcp_slug = profile_data_response["mcp_slug"]

        # 3. Make MCP tool calls
        tools = ["get_basic_info", "get_skills", "get_basic_info"]  # Call basic_info twice
        for i, tool in enumerate(tools):
            response = client.post(f"/mcp/{mcp_slug}", json={
                "jsonrpc": "2.0",
                "id": i,
                "method": "tools/call",
                "params": {"name": tool}
            })
            assert response.status_code == 200

        # 4. Verify metrics
        metrics_response = client.get("/metrics/dashboard?hours=1", headers=headers)
        assert metrics_response.status_code == 200

        dashboard = metrics_response.json()

        # Should have tool statistics
        assert dashboard["tools"]["total_calls"] >= 3

        # Should have user activity
        assert dashboard["users"]["total_users"] >= 1

    def test_error_tracking_workflow(self, client):
        """Test error tracking workflow"""
        # Create user
        unique_email = f"error_workflow{uuid.uuid4().hex[:8]}@example.com"
        register_data = {
            "email": unique_email,
            "password": "password123",
            "preferred_name": "erroruser"
        }

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
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create profile
        profile_data = {
            "basic_info": {
                "name": "Error Test",
                "title": "QA",
                "email": unique_email,
                "summary": "Testing errors"
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

        profile_response = client.post("/profile/create", json=profile_data, headers=headers)
        assert profile_response.status_code == 200, f"Profile creation failed: {profile_response.json()}"

        profile_data_response = profile_response.json()
        assert "mcp_slug" in profile_data_response, f"No mcp_slug in response: {profile_data_response}"
        mcp_slug = profile_data_response["mcp_slug"]

        # Make some failed calls
        client.post(f"/mcp/{mcp_slug}", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "invalid_tool"}
        })

        # Check error metrics
        error_response = client.get("/metrics/errors?hours=1", headers=headers)
        assert error_response.status_code == 200

        errors = error_response.json()
        assert errors["total_errors"] >= 1
