import pytest
import time
from datetime import datetime, timedelta
from app.core.observability import (
    MetricsCollector,
    ToolMetrics,
    PerformanceMetrics,
    get_metrics_collector,
    track_performance,
    record_tool_call
)


class TestToolMetrics:
    """Test ToolMetrics dataclass"""

    def test_tool_metrics_creation(self):
        """Test creating ToolMetrics instance"""
        metrics = ToolMetrics(
            tool_name="get_basic_info",
            user_slug="test-user",
            timestamp=datetime.utcnow().isoformat(),
            duration_ms=15.5,
            success=True,
            request_id=1
        )

        assert metrics.tool_name == "get_basic_info"
        assert metrics.user_slug == "test-user"
        assert metrics.duration_ms == 15.5
        assert metrics.success is True
        assert metrics.request_id == 1
        assert metrics.error_message is None

    def test_tool_metrics_with_error(self):
        """Test ToolMetrics with error message"""
        metrics = ToolMetrics(
            tool_name="get_projects",
            user_slug="test-user",
            timestamp=datetime.utcnow().isoformat(),
            duration_ms=10.2,
            success=False,
            error_message="Database connection failed"
        )

        assert metrics.success is False
        assert metrics.error_message == "Database connection failed"


class TestPerformanceMetrics:
    """Test PerformanceMetrics dataclass"""

    def test_performance_metrics_creation(self):
        """Test creating PerformanceMetrics instance"""
        metrics = PerformanceMetrics(
            operation="initialize",
            duration_ms=25.3,
            timestamp=datetime.utcnow().isoformat(),
            user_slug="test-user",
            success=True
        )

        assert metrics.operation == "initialize"
        assert metrics.duration_ms == 25.3
        assert metrics.success is True
        assert metrics.error is None


class TestMetricsCollector:
    """Test MetricsCollector functionality"""

    @pytest.fixture
    def collector(self):
        """Create a fresh MetricsCollector instance for each test"""
        return MetricsCollector()

    @pytest.fixture
    def sample_tool_metrics(self):
        """Create sample tool metrics"""
        return ToolMetrics(
            tool_name="get_basic_info",
            user_slug="user-123",
            timestamp=datetime.utcnow().isoformat(),
            duration_ms=12.5,
            success=True,
            request_id=1
        )

    @pytest.fixture
    def sample_performance_metrics(self):
        """Create sample performance metrics"""
        return PerformanceMetrics(
            operation="tools/call",
            duration_ms=15.8,
            timestamp=datetime.utcnow().isoformat(),
            user_slug="user-123",
            success=True
        )

    def test_record_tool_call(self, collector, sample_tool_metrics):
        """Test recording a tool call"""
        collector.record_tool_call(sample_tool_metrics)

        assert len(collector._tool_metrics) == 1
        assert collector._tool_usage_count["get_basic_info"] == 1
        assert collector._user_activity["user-123"] == 1

    def test_record_multiple_tool_calls(self, collector):
        """Test recording multiple tool calls"""
        for i in range(5):
            metrics = ToolMetrics(
                tool_name="get_basic_info",
                user_slug="user-123",
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=10.0 + i,
                success=True,
                request_id=i
            )
            collector.record_tool_call(metrics)

        assert len(collector._tool_metrics) == 5
        assert collector._tool_usage_count["get_basic_info"] == 5
        assert collector._user_activity["user-123"] == 5

    def test_record_failed_tool_call(self, collector):
        """Test recording a failed tool call"""
        metrics = ToolMetrics(
            tool_name="get_projects",
            user_slug="user-456",
            timestamp=datetime.utcnow().isoformat(),
            duration_ms=8.3,
            success=False,
            error_message="Tool not found",
            request_id=2
        )
        collector.record_tool_call(metrics)

        assert collector._tool_errors["get_projects"] == 1
        assert collector._user_activity["user-456"] == 1

    def test_record_performance(self, collector, sample_performance_metrics):
        """Test recording performance metrics"""
        collector.record_performance(sample_performance_metrics)

        assert len(collector._performance_metrics) == 1

    def test_get_tool_statistics_empty(self, collector):
        """Test getting statistics with no data"""
        stats = collector.get_tool_statistics(hours=24)

        assert stats["total_calls"] == 0
        assert stats["period_hours"] == 24
        assert stats["tools"] == {}

    def test_get_tool_statistics_with_data(self, collector):
        """Test getting tool statistics with data"""
        # Add multiple tool calls
        for i in range(3):
            metrics = ToolMetrics(
                tool_name="get_basic_info",
                user_slug="user-123",
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=10.0 + i * 2,
                success=True,
                request_id=i
            )
            collector.record_tool_call(metrics)

        # Add one failed call
        failed_metrics = ToolMetrics(
            tool_name="get_basic_info",
            user_slug="user-456",
            timestamp=datetime.utcnow().isoformat(),
            duration_ms=5.0,
            success=False,
            error_message="Error",
            request_id=3
        )
        collector.record_tool_call(failed_metrics)

        stats = collector.get_tool_statistics(hours=24)

        assert stats["total_calls"] == 4
        assert stats["unique_users"] == 2
        assert "get_basic_info" in stats["tools"]

        tool_stats = stats["tools"]["get_basic_info"]
        assert tool_stats["total_calls"] == 4
        assert tool_stats["successful_calls"] == 3
        assert tool_stats["failed_calls"] == 1
        assert tool_stats["avg_duration_ms"] > 0
        assert tool_stats["min_duration_ms"] == 5.0
        assert tool_stats["max_duration_ms"] == 14.0

    def test_get_user_activity(self, collector):
        """Test getting user activity statistics"""
        # Add calls from multiple users
        users = ["user-1", "user-2", "user-1"]
        tools = ["get_basic_info", "get_skills", "get_projects"]

        for user, tool in zip(users, tools):
            metrics = ToolMetrics(
                tool_name=tool,
                user_slug=user,
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=10.0,
                success=True,
                request_id=1
            )
            collector.record_tool_call(metrics)

        activity = collector.get_user_activity(hours=24)

        assert activity["total_users"] == 2
        assert activity["period_hours"] == 24
        assert "user-1" in activity["users"]
        assert "user-2" in activity["users"]

        user1_stats = activity["users"]["user-1"]
        assert user1_stats["total_calls"] == 2
        assert user1_stats["unique_tools"] == 2
        assert user1_stats["successful_calls"] == 2
        assert user1_stats["failed_calls"] == 0

    def test_get_performance_summary(self, collector):
        """Test getting performance summary"""
        # Add performance metrics
        for i in range(3):
            metrics = PerformanceMetrics(
                operation="tools/call",
                duration_ms=10.0 + i * 5,
                timestamp=datetime.utcnow().isoformat(),
                user_slug="user-123",
                success=True
            )
            collector.record_performance(metrics)

        summary = collector.get_performance_summary(hours=24)

        assert summary["total_operations"] == 3
        assert "tools/call" in summary["operations"]

        op_stats = summary["operations"]["tools/call"]
        assert op_stats["count"] == 3
        assert op_stats["avg_duration_ms"] > 0
        assert op_stats["success_rate"] == 100.0

    def test_get_error_summary(self, collector):
        """Test getting error summary"""
        # Add successful and failed calls
        for i in range(2):
            metrics = ToolMetrics(
                tool_name="get_basic_info",
                user_slug="user-123",
                timestamp=datetime.utcnow().isoformat(),
                duration_ms=10.0,
                success=False,
                error_message=f"Error {i}",
                request_id=i
            )
            collector.record_tool_call(metrics)

        errors = collector.get_error_summary(hours=24)

        assert errors["total_errors"] == 2
        assert "get_basic_info" in errors["errors_by_tool"]

        tool_errors = errors["errors_by_tool"]["get_basic_info"]
        assert tool_errors["count"] == 2
        assert len(tool_errors["errors"]) == 2

    def test_clear_old_metrics(self, collector):
        """Test clearing old metrics"""
        # Add old metrics (25 hours ago)
        old_time = (datetime.utcnow() - timedelta(hours=25)).isoformat()
        old_metrics = ToolMetrics(
            tool_name="get_basic_info",
            user_slug="user-123",
            timestamp=old_time,
            duration_ms=10.0,
            success=True,
            request_id=1
        )
        collector.record_tool_call(old_metrics)

        # Add recent metrics
        recent_metrics = ToolMetrics(
            tool_name="get_skills",
            user_slug="user-456",
            timestamp=datetime.utcnow().isoformat(),
            duration_ms=12.0,
            success=True,
            request_id=2
        )
        collector.record_tool_call(recent_metrics)

        assert len(collector._tool_metrics) == 2

        # Clear metrics older than 24 hours
        collector.clear_old_metrics(hours=24)

        # Should only have recent metrics
        assert len(collector._tool_metrics) == 1
        assert collector._tool_metrics[0].tool_name == "get_skills"

    def test_time_filtering(self, collector):
        """Test that statistics are properly filtered by time"""
        # Add old metrics (2 days ago)
        old_time = (datetime.utcnow() - timedelta(hours=48)).isoformat()
        old_metrics = ToolMetrics(
            tool_name="get_basic_info",
            user_slug="user-old",
            timestamp=old_time,
            duration_ms=10.0,
            success=True,
            request_id=1
        )
        collector.record_tool_call(old_metrics)

        # Add recent metrics (1 hour ago)
        recent_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        recent_metrics = ToolMetrics(
            tool_name="get_skills",
            user_slug="user-recent",
            timestamp=recent_time,
            duration_ms=12.0,
            success=True,
            request_id=2
        )
        collector.record_tool_call(recent_metrics)

        # Get stats for last 24 hours
        stats = collector.get_tool_statistics(hours=24)

        # Should only include recent metrics
        assert stats["total_calls"] == 1
        assert "get_skills" in stats["tools"]
        assert "get_basic_info" not in stats["tools"]


class TestTrackPerformanceDecorator:
    """Test the track_performance decorator"""

    def test_async_function_tracking(self):
        """Test tracking async function performance"""
        import asyncio

        collector = get_metrics_collector()
        initial_count = len(collector._performance_metrics)

        @track_performance("test_async_operation")
        async def async_function(user_slug: str):
            await asyncio.sleep(0.01)
            return "success"

        # Run async function in event loop
        result = asyncio.run(async_function(user_slug="test-user"))

        assert result == "success"
        assert len(collector._performance_metrics) > initial_count

    def test_sync_function_tracking(self):
        """Test tracking sync function performance"""
        collector = get_metrics_collector()
        initial_count = len(collector._performance_metrics)

        @track_performance("test_sync_operation")
        def sync_function(user_slug: str):
            time.sleep(0.01)
            return "success"

        result = sync_function(user_slug="test-user")

        assert result == "success"
        assert len(collector._performance_metrics) > initial_count

    def test_function_with_exception(self):
        """Test tracking function that raises exception"""
        import asyncio

        collector = get_metrics_collector()
        initial_count = len(collector._performance_metrics)

        @track_performance("test_error_operation")
        async def failing_function(user_slug: str):
            raise ValueError("Test error")

        # Run async function that raises exception
        with pytest.raises(ValueError):
            asyncio.run(failing_function(user_slug="test-user"))

        # Should still record metrics
        assert len(collector._performance_metrics) > initial_count

        # Check that error was recorded
        latest_metric = collector._performance_metrics[-1]
        assert latest_metric.success is False
        assert latest_metric.error == "Test error"


class TestRecordToolCallHelper:
    """Test the record_tool_call helper function"""

    def test_record_successful_call(self):
        """Test recording successful tool call"""
        collector = get_metrics_collector()
        initial_count = len(collector._tool_metrics)

        record_tool_call(
            tool_name="get_basic_info",
            user_slug="test-user",
            duration_ms=15.5,
            success=True,
            request_id=1
        )

        assert len(collector._tool_metrics) > initial_count

        latest_metric = collector._tool_metrics[-1]
        assert latest_metric.tool_name == "get_basic_info"
        assert latest_metric.user_slug == "test-user"
        assert latest_metric.duration_ms == 15.5
        assert latest_metric.success is True

    def test_record_failed_call(self):
        """Test recording failed tool call"""
        collector = get_metrics_collector()
        initial_count = len(collector._tool_metrics)

        record_tool_call(
            tool_name="get_projects",
            user_slug="test-user",
            duration_ms=8.3,
            success=False,
            error_message="Tool not found",
            request_id=2
        )

        assert len(collector._tool_metrics) > initial_count

        latest_metric = collector._tool_metrics[-1]
        assert latest_metric.success is False
        assert latest_metric.error_message == "Tool not found"


class TestMetricsCollectorSingleton:
    """Test that get_metrics_collector returns the same instance"""

    def test_singleton_instance(self):
        """Test that get_metrics_collector returns same instance"""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()

        assert collector1 is collector2

    def test_shared_state(self):
        """Test that metrics are shared across collector instances"""
        collector1 = get_metrics_collector()

        record_tool_call(
            tool_name="test_tool",
            user_slug="test-user",
            duration_ms=10.0,
            success=True,
            request_id=1
        )

        collector2 = get_metrics_collector()
        stats = collector2.get_tool_statistics(hours=24)

        # Should see the metrics we just added
        assert stats["total_calls"] > 0


# Import asyncio for async tests
import asyncio
