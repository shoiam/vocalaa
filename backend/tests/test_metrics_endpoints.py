import pytest
import uuid
from fastapi.testclient import TestClient
from app.core.observability import get_metrics_collector, record_tool_call
from datetime import datetime


class TestMetricsEndpoints:
    """Test metrics API endpoints"""

    @pytest.fixture
    def auth_headers(self, client):
        """Create authenticated user and return auth headers"""
        # Register user
        unique_email = f"metrics_test{uuid.uuid4().hex[:8]}@example.com"
        register_data = {
            "email": unique_email,
            "password": "password123",
            "preferred_name": "metricsuser"
        }

        client.post("/auth/register", json=register_data)

        # Login to get token
        login_response = client.post("/auth/login", json={
            "email": unique_email,
            "password": "password123"
        })

        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    def populated_metrics(self):
        """Populate some test metrics"""
        collector = get_metrics_collector()

        # Add some tool call metrics
        for i in range(5):
            record_tool_call(
                tool_name="get_basic_info",
                user_slug=f"test-user-{i % 2}",
                duration_ms=10.0 + i,
                success=True,
                request_id=i
            )

        # Add some failed calls
        for i in range(2):
            record_tool_call(
                tool_name="get_projects",
                user_slug="test-user-error",
                duration_ms=5.0,
                success=False,
                error_message=f"Error {i}",
                request_id=i + 100
            )

        yield collector

        # Note: In a real scenario, you might want to clear metrics after tests
        # collector.clear_old_metrics(hours=0)


class TestToolsEndpoint(TestMetricsEndpoints):
    """Test /metrics/tools endpoint"""

    def test_get_tool_statistics_requires_auth(self, client):
        """Test that metrics endpoint requires authentication"""
        response = client.get("/metrics/tools")
        assert response.status_code == 403

    def test_get_tool_statistics_with_auth(self, client, auth_headers, populated_metrics):
        """Test getting tool statistics with authentication"""
        response = client.get("/metrics/tools", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "period_hours" in data
        assert "total_calls" in data
        assert "unique_users" in data
        assert "tools" in data
        assert data["period_hours"] == 24

    def test_get_tool_statistics_with_custom_hours(self, client, auth_headers, populated_metrics):
        """Test getting tool statistics with custom time period"""
        response = client.get("/metrics/tools?hours=48", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["period_hours"] == 48

    def test_get_tool_statistics_invalid_hours(self, client, auth_headers):
        """Test validation of hours parameter"""
        # Too small
        response = client.get("/metrics/tools?hours=0", headers=auth_headers)
        assert response.status_code == 422

        # Too large
        response = client.get("/metrics/tools?hours=200", headers=auth_headers)
        assert response.status_code == 422

    def test_tool_statistics_structure(self, client, auth_headers, populated_metrics):
        """Test the structure of tool statistics response"""
        response = client.get("/metrics/tools", headers=auth_headers)
        data = response.json()

        assert isinstance(data["tools"], dict)

        # Check if we have the tools we added
        if "get_basic_info" in data["tools"]:
            tool_stats = data["tools"]["get_basic_info"]
            assert "total_calls" in tool_stats
            assert "successful_calls" in tool_stats
            assert "failed_calls" in tool_stats
            assert "avg_duration_ms" in tool_stats
            assert "min_duration_ms" in tool_stats
            assert "max_duration_ms" in tool_stats


class TestUsersEndpoint(TestMetricsEndpoints):
    """Test /metrics/users endpoint"""

    def test_get_user_activity_requires_auth(self, client):
        """Test that users endpoint requires authentication"""
        response = client.get("/metrics/users")
        assert response.status_code == 403

    def test_get_user_activity_with_auth(self, client, auth_headers, populated_metrics):
        """Test getting user activity with authentication"""
        response = client.get("/metrics/users", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "period_hours" in data
        assert "total_users" in data
        assert "users" in data

    def test_get_user_activity_with_custom_hours(self, client, auth_headers, populated_metrics):
        """Test getting user activity with custom time period"""
        response = client.get("/metrics/users?hours=72", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["period_hours"] == 72

    def test_user_activity_structure(self, client, auth_headers, populated_metrics):
        """Test the structure of user activity response"""
        response = client.get("/metrics/users", headers=auth_headers)
        data = response.json()

        assert isinstance(data["users"], dict)

        # Check structure of user stats if we have any
        if data["total_users"] > 0:
            # Get first user's stats
            first_user = list(data["users"].values())[0]
            assert "total_calls" in first_user
            assert "tools_used" in first_user
            assert "unique_tools" in first_user
            assert "successful_calls" in first_user
            assert "failed_calls" in first_user
            assert "last_activity" in first_user


class TestPerformanceEndpoint(TestMetricsEndpoints):
    """Test /metrics/performance endpoint"""

    def test_get_performance_summary_requires_auth(self, client):
        """Test that performance endpoint requires authentication"""
        response = client.get("/metrics/performance")
        assert response.status_code == 403

    def test_get_performance_summary_with_auth(self, client, auth_headers):
        """Test getting performance summary with authentication"""
        response = client.get("/metrics/performance", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "period_hours" in data
        assert "total_operations" in data
        assert "operations" in data

    def test_get_performance_summary_with_custom_hours(self, client, auth_headers):
        """Test getting performance summary with custom time period"""
        response = client.get("/metrics/performance?hours=96", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["period_hours"] == 96

    def test_performance_summary_structure(self, client, auth_headers):
        """Test the structure of performance summary response"""
        response = client.get("/metrics/performance", headers=auth_headers)
        data = response.json()

        assert isinstance(data["operations"], dict)

        # Check structure if we have operations
        if data["total_operations"] > 0:
            first_op = list(data["operations"].values())[0]
            assert "count" in first_op
            assert "avg_duration_ms" in first_op
            assert "min_duration_ms" in first_op
            assert "max_duration_ms" in first_op
            assert "success_rate" in first_op


class TestErrorsEndpoint(TestMetricsEndpoints):
    """Test /metrics/errors endpoint"""

    def test_get_error_summary_requires_auth(self, client):
        """Test that errors endpoint requires authentication"""
        response = client.get("/metrics/errors")
        assert response.status_code == 403

    def test_get_error_summary_with_auth(self, client, auth_headers, populated_metrics):
        """Test getting error summary with authentication"""
        response = client.get("/metrics/errors", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "period_hours" in data
        assert "total_errors" in data
        assert "errors_by_tool" in data

    def test_get_error_summary_with_custom_hours(self, client, auth_headers):
        """Test getting error summary with custom time period"""
        response = client.get("/metrics/errors?hours=120", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["period_hours"] == 120

    def test_error_summary_structure(self, client, auth_headers, populated_metrics):
        """Test the structure of error summary response"""
        response = client.get("/metrics/errors", headers=auth_headers)
        data = response.json()

        assert isinstance(data["errors_by_tool"], dict)

        # Check structure if we have errors
        if data["total_errors"] > 0:
            # Should have get_projects errors from populated_metrics
            if "get_projects" in data["errors_by_tool"]:
                tool_errors = data["errors_by_tool"]["get_projects"]
                assert "count" in tool_errors
                assert "errors" in tool_errors
                assert isinstance(tool_errors["errors"], list)

                if len(tool_errors["errors"]) > 0:
                    first_error = tool_errors["errors"][0]
                    assert "timestamp" in first_error
                    assert "user_slug" in first_error
                    assert "error_message" in first_error


class TestDashboardEndpoint(TestMetricsEndpoints):
    """Test /metrics/dashboard endpoint"""

    def test_get_dashboard_requires_auth(self, client):
        """Test that dashboard endpoint requires authentication"""
        response = client.get("/metrics/dashboard")
        assert response.status_code == 403

    def test_get_dashboard_with_auth(self, client, auth_headers, populated_metrics):
        """Test getting metrics dashboard with authentication"""
        response = client.get("/metrics/dashboard", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should contain all metric types
        assert "period_hours" in data
        assert "tools" in data
        assert "users" in data
        assert "performance" in data
        assert "errors" in data

    def test_get_dashboard_with_custom_hours(self, client, auth_headers):
        """Test getting dashboard with custom time period"""
        response = client.get("/metrics/dashboard?hours=168", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["period_hours"] == 168

    def test_dashboard_comprehensive_structure(self, client, auth_headers, populated_metrics):
        """Test that dashboard contains complete data structure"""
        response = client.get("/metrics/dashboard", headers=auth_headers)
        data = response.json()

        # Verify tools section
        assert "total_calls" in data["tools"]
        assert "tools" in data["tools"]

        # Verify users section
        assert "total_users" in data["users"]
        assert "users" in data["users"]

        # Verify performance section
        assert "total_operations" in data["performance"]
        assert "operations" in data["performance"]

        # Verify errors section
        assert "total_errors" in data["errors"]
        assert "errors_by_tool" in data["errors"]


class TestClearMetricsEndpoint(TestMetricsEndpoints):
    """Test /metrics/clear endpoint"""

    def test_clear_metrics_requires_auth(self, client):
        """Test that clear endpoint requires authentication"""
        response = client.post("/metrics/clear")
        assert response.status_code == 403

    def test_clear_metrics_with_auth(self, client, auth_headers):
        """Test clearing metrics with authentication"""
        response = client.post("/metrics/clear", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "cleared_by" in data
        assert "Successfully cleared metrics" in data["message"]

    def test_clear_metrics_with_custom_hours(self, client, auth_headers):
        """Test clearing metrics with custom retention period"""
        response = client.post("/metrics/clear?hours=240", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "240 hours" in data["message"]

    def test_clear_metrics_validation(self, client, auth_headers):
        """Test validation of clear metrics hours parameter"""
        # Too small (less than 24)
        response = client.post("/metrics/clear?hours=12", headers=auth_headers)
        assert response.status_code == 422

        # Too large (more than 720)
        response = client.post("/metrics/clear?hours=1000", headers=auth_headers)
        assert response.status_code == 422

    def test_clear_metrics_preserves_recent_data(self, client, auth_headers):
        """Test that clearing old metrics preserves recent data"""
        # Add some recent metrics
        record_tool_call(
            tool_name="test_tool",
            user_slug="recent-user",
            duration_ms=10.0,
            success=True,
            request_id=999
        )

        # Get current stats
        response_before = client.get("/metrics/tools?hours=24", headers=auth_headers)
        calls_before = response_before.json()["total_calls"]

        # Clear very old metrics (30 days)
        client.post("/metrics/clear?hours=720", headers=auth_headers)

        # Check that recent data is still there
        response_after = client.get("/metrics/tools?hours=24", headers=auth_headers)
        calls_after = response_after.json()["total_calls"]

        # Should have at least the call we just made
        assert calls_after >= 1


class TestMetricsEndpointEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def auth_headers(self, client):
        """Create authenticated user and return auth headers"""
        unique_email = f"edge_test{uuid.uuid4().hex[:8]}@example.com"
        register_data = {
            "email": unique_email,
            "password": "password123",
            "preferred_name": "edgeuser"
        }

        client.post("/auth/register", json=register_data)
        login_response = client.post("/auth/login", json={
            "email": unique_email,
            "password": "password123"
        })

        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_invalid_auth_token(self, client):
        """Test endpoints with invalid auth token"""
        headers = {"Authorization": "Bearer invalid_token"}

        endpoints = [
            "/metrics/tools",
            "/metrics/users",
            "/metrics/performance",
            "/metrics/errors",
            "/metrics/dashboard"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint, headers=headers)
            assert response.status_code in [401, 403]

    def test_missing_auth_header(self, client):
        """Test endpoints without auth header"""
        response = client.get("/metrics/tools")
        assert response.status_code == 403

    def test_metrics_with_no_data(self, client, auth_headers):
        """Test metrics endpoints when no data is available"""
        # Clear all metrics first
        collector = get_metrics_collector()
        collector.clear_old_metrics(hours=0)

        # All endpoints should still return valid responses
        response = client.get("/metrics/tools", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_calls"] == 0

        response = client.get("/metrics/users", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_users"] == 0

    def test_concurrent_requests(self, client, auth_headers):
        """Test handling of concurrent metric requests"""
        import concurrent.futures

        def make_request():
            return client.get("/metrics/dashboard", headers=auth_headers)

        # Make multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All requests should succeed
        for response in results:
            assert response.status_code == 200

    def test_options_method_support(self, client):
        """Test that endpoints support OPTIONS for CORS"""
        # Note: This depends on your CORS configuration
        response = client.options("/metrics/tools")
        # OPTIONS is typically allowed for CORS, but may return 200 or 405
        # For now, just verify the endpoint exists and returns a response
        assert response is not None
        # If CORS is configured, should return 200, otherwise might be 405
        assert response.status_code in [200, 204, 405]
