import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from functools import wraps
from collections import defaultdict
from loguru import logger
import json
from dataclasses import dataclass, asdict


@dataclass
class ToolMetrics:
    """Metrics for a single tool invocation"""
    tool_name: str
    user_slug: str
    timestamp: str
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    request_id: Optional[int] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics for MCP operations"""
    operation: str
    duration_ms: float
    timestamp: str
    user_slug: Optional[str] = None
    success: bool = True
    error: Optional[str] = None


class MetricsCollector:
    """
    Centralized metrics collector for MCP operations
    Tracks tool usage, performance, and errors
    """

    def __init__(self):
        self._tool_metrics: List[ToolMetrics] = []
        self._performance_metrics: List[PerformanceMetrics] = []
        self._tool_usage_count: Dict[str, int] = defaultdict(int)
        self._tool_errors: Dict[str, int] = defaultdict(int)
        self._user_activity: Dict[str, int] = defaultdict(int)

    def record_tool_call(self, metrics: ToolMetrics) -> None:
        """Record a tool call with its metrics"""
        self._tool_metrics.append(metrics)
        self._tool_usage_count[metrics.tool_name] += 1
        self._user_activity[metrics.user_slug] += 1

        if not metrics.success:
            self._tool_errors[metrics.tool_name] += 1

        # Log structured metrics
        logger.info(
            "MCP_TOOL_CALL",
            extra={
                "tool": metrics.tool_name,
                "user": metrics.user_slug,
                "duration_ms": metrics.duration_ms,
                "success": metrics.success,
                "timestamp": metrics.timestamp
            }
        )

    def record_performance(self, metrics: PerformanceMetrics) -> None:
        """Record performance metrics for an operation"""
        self._performance_metrics.append(metrics)

        # Log performance data
        logger.info(
            "MCP_PERFORMANCE",
            extra={
                "operation": metrics.operation,
                "duration_ms": metrics.duration_ms,
                "user": metrics.user_slug,
                "success": metrics.success,
                "timestamp": metrics.timestamp
            }
        )

    def get_tool_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get tool usage statistics for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        recent_metrics = [
            m for m in self._tool_metrics
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]

        if not recent_metrics:
            return {
                "period_hours": hours,
                "total_calls": 0,
                "tools": {}
            }

        tool_stats = defaultdict(lambda: {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "avg_duration_ms": 0,
            "min_duration_ms": float('inf'),
            "max_duration_ms": 0,
            "total_duration_ms": 0
        })

        for metric in recent_metrics:
            stats = tool_stats[metric.tool_name]
            stats["total_calls"] += 1

            if metric.success:
                stats["successful_calls"] += 1
            else:
                stats["failed_calls"] += 1

            stats["total_duration_ms"] += metric.duration_ms
            stats["min_duration_ms"] = min(stats["min_duration_ms"], metric.duration_ms)
            stats["max_duration_ms"] = max(stats["max_duration_ms"], metric.duration_ms)

        # Calculate averages
        for tool, stats in tool_stats.items():
            if stats["total_calls"] > 0:
                stats["avg_duration_ms"] = round(stats["total_duration_ms"] / stats["total_calls"], 2)
            del stats["total_duration_ms"]  # Remove from output

        return {
            "period_hours": hours,
            "total_calls": len(recent_metrics),
            "unique_users": len(set(m.user_slug for m in recent_metrics)),
            "tools": dict(tool_stats)
        }

    def get_user_activity(self, hours: int = 24) -> Dict[str, Any]:
        """Get user activity statistics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        recent_metrics = [
            m for m in self._tool_metrics
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]

        user_stats = defaultdict(lambda: {
            "total_calls": 0,
            "tools_used": set(),
            "successful_calls": 0,
            "failed_calls": 0,
            "last_activity": None
        })

        for metric in recent_metrics:
            stats = user_stats[metric.user_slug]
            stats["total_calls"] += 1
            stats["tools_used"].add(metric.tool_name)

            if metric.success:
                stats["successful_calls"] += 1
            else:
                stats["failed_calls"] += 1

            # Track last activity
            if stats["last_activity"] is None or metric.timestamp > stats["last_activity"]:
                stats["last_activity"] = metric.timestamp

        # Convert sets to lists for JSON serialization
        for user, stats in user_stats.items():
            stats["tools_used"] = list(stats["tools_used"])
            stats["unique_tools"] = len(stats["tools_used"])

        return {
            "period_hours": hours,
            "total_users": len(user_stats),
            "users": dict(user_stats)
        }

    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for all operations"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        recent_metrics = [
            m for m in self._performance_metrics
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]

        if not recent_metrics:
            return {
                "period_hours": hours,
                "total_operations": 0,
                "operations": {}
            }

        operation_stats = defaultdict(lambda: {
            "count": 0,
            "avg_duration_ms": 0,
            "min_duration_ms": float('inf'),
            "max_duration_ms": 0,
            "success_rate": 0,
            "total_duration": 0,
            "successful": 0
        })

        for metric in recent_metrics:
            stats = operation_stats[metric.operation]
            stats["count"] += 1
            stats["total_duration"] += metric.duration_ms
            stats["min_duration_ms"] = min(stats["min_duration_ms"], metric.duration_ms)
            stats["max_duration_ms"] = max(stats["max_duration_ms"], metric.duration_ms)

            if metric.success:
                stats["successful"] += 1

        # Calculate averages and success rates
        for operation, stats in operation_stats.items():
            if stats["count"] > 0:
                stats["avg_duration_ms"] = round(stats["total_duration"] / stats["count"], 2)
                stats["success_rate"] = round((stats["successful"] / stats["count"]) * 100, 2)
            del stats["total_duration"]
            del stats["successful"]

        return {
            "period_hours": hours,
            "total_operations": len(recent_metrics),
            "operations": dict(operation_stats)
        }

    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for failed operations"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        recent_errors = [
            m for m in self._tool_metrics
            if not m.success and datetime.fromisoformat(m.timestamp) > cutoff_time
        ]

        error_by_tool = defaultdict(lambda: {
            "count": 0,
            "errors": []
        })

        for metric in recent_errors:
            error_by_tool[metric.tool_name]["count"] += 1
            error_by_tool[metric.tool_name]["errors"].append({
                "timestamp": metric.timestamp,
                "user_slug": metric.user_slug,
                "error_message": metric.error_message
            })

        return {
            "period_hours": hours,
            "total_errors": len(recent_errors),
            "errors_by_tool": dict(error_by_tool)
        }

    def clear_old_metrics(self, hours: int = 168) -> None:
        """Clear metrics older than specified hours (default: 7 days)"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        self._tool_metrics = [
            m for m in self._tool_metrics
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]

        self._performance_metrics = [
            m for m in self._performance_metrics
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]

        logger.info(f"Cleared metrics older than {hours} hours")


# Global metrics collector instance
_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    return _metrics_collector


def track_performance(operation: str):
    """
    Decorator to track performance of MCP operations

    Usage:
        @track_performance("initialize")
        async def handle_initialize():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000

                # Extract user_slug if available in args/kwargs
                user_slug = kwargs.get('user_slug') or kwargs.get('user_profile', {}).get('mcp_slug')

                metrics = PerformanceMetrics(
                    operation=operation,
                    duration_ms=round(duration_ms, 2),
                    timestamp=datetime.utcnow().isoformat(),
                    user_slug=user_slug,
                    success=success,
                    error=error
                )

                _metrics_collector.record_performance(metrics)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000

                user_slug = kwargs.get('user_slug') or kwargs.get('user_profile', {}).get('mcp_slug')

                metrics = PerformanceMetrics(
                    operation=operation,
                    duration_ms=round(duration_ms, 2),
                    timestamp=datetime.utcnow().isoformat(),
                    user_slug=user_slug,
                    success=success,
                    error=error
                )

                _metrics_collector.record_performance(metrics)

        # Return appropriate wrapper based on whether function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def record_tool_call(
    tool_name: str,
    user_slug: str,
    duration_ms: float,
    success: bool,
    error_message: Optional[str] = None,
    request_id: Optional[int] = None
) -> None:
    """
    Helper function to record a tool call
    """
    metrics = ToolMetrics(
        tool_name=tool_name,
        user_slug=user_slug,
        timestamp=datetime.utcnow().isoformat(),
        duration_ms=round(duration_ms, 2),
        success=success,
        error_message=error_message,
        request_id=request_id
    )

    _metrics_collector.record_tool_call(metrics)
